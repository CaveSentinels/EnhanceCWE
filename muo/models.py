from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models, transaction
from django.conf import settings
from cwe.models import CWE
from base.models import BaseModel
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from signals import *
from django.utils import timezone

STATUS = [('draft', 'Draft'),
          ('in_review', 'In Review'),
          ('approved', 'Approved'),
          ('rejected', 'Rejected')]

ISSUE_TYPES = [('incorrect', 'Incorrect Content'),
                ('spam', 'Spam'),
                ('duplicate', 'Duplicate')]

ISSUE_STATUS = [('open', 'Open'),
                 ('investigating', 'Investigating'),
                 ('resolved', 'Resolved')]


class Tag(BaseModel):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        default_permissions = ('add', 'change', 'delete', 'view')

    def __unicode__(self):
        return self.name


class MisuseCase(BaseModel):
    name = models.CharField(max_length=16, null=True, blank=True, db_index=True, default="/")
    description = models.TextField()
    cwes = models.ManyToManyField(CWE, related_name='misuse_cases')
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = "Misuse Case"
        verbose_name_plural = "Misuse Cases"

    def __unicode__(self):
        return "%s - %s..." % (self.name, self.description[:70])


@receiver(post_save, sender=MisuseCase, dispatch_uid='misusecase_post_save_signal')
def post_save_misusecase(sender, instance, created, using, **kwargs):
    """ Set the value of the field 'name' after creating the object """
    if created:
        instance.name = "MU/{0:05d}".format(instance.id)
        instance.save()


class MUOContainer(BaseModel):
    name = models.CharField(max_length=16, null=True, blank=True, db_index=True, default="/")
    cwes = models.ManyToManyField(CWE, related_name='muo_container')
    misuse_case = models.ForeignKey(MisuseCase, on_delete=models.PROTECT)
    new_misuse_case = models.TextField(null=True, blank=True)
    reject_reason = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=64, default='draft')
    is_custom = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "MUO Container"
        verbose_name_plural = "MUO Containers"
        # additional permissions
        permissions = (
            ('can_approve', 'Can approve MUO container'),
            ('can_reject', 'Can reject MUO container'),
            ('can_view_all', 'Can view all MUO container'),
        )

    @staticmethod
    def create_custom_muo(cwe_ids, misusecase, usecase, osr, created_by):
        '''
        This is a static method that creates a custom MUO. It also established the relationship between the
        objects that has to be related on MUO creation i.e. relationship between cwes and misuse case, cwes
        and muo container, misuse case and muo container, misuse cae and use case.
        :param cwe_ids: (LIST of Integers) List of CWE IDs
        :param misusecase: (TEXT) Description of the misuse case
        :param usecase: (TEXT) Description of the use case
        :param osr: (TEXT) Description of the osr
        :param created_by: (USER)
        :return: Void
        '''
        cwe_objects = list(CWE.objects.filter(pk__in=cwe_ids))

        if len(cwe_objects) != len(cwe_ids):
            # The count of objects returned from the database for the CWE ids passed didn't match the
            # count of the the list of cwe ids. This means some of the IDs were invalid and don't exist
            # in the database.
            raise ValueError("Looks like there are CWE IDs, which are not valid")

        with transaction.atomic():
            # This block should be inside the atmoic context manager because if any of the database transaction
            # fails, all the previous database transaction must be rolled back

            # Create the misuse case and establish the relationship with the CWEs
            misuse_case = MisuseCase(description=misusecase,
                                     created_by=created_by,
                                     created_at=timezone.now())
            misuse_case.save()
            misuse_case.cwes.add(*cwe_objects)  # Establish the relationship between the misuse case and CWEs

            # Create the MUO container for the misuse case and establish the relationship between the
            # MUO Container and CWEs
            muo_container = MUOContainer(is_custom=True,
                                         status='draft',
                                         misuse_case=misuse_case,
                                         created_by=created_by,
                                         created_at=timezone.now())
            muo_container.save()
            muo_container.cwes.add(*cwe_objects) # Establish the relationship between the muo container and cwes

            # Create the Use case for the Misuse Case and MUO Container
            use_case = UseCase(description=usecase,
                               osr=osr,
                               muo_container=muo_container,
                               misuse_case=misuse_case,
                               created_by=created_by,
                               created_at=timezone.now())
            use_case.save()


    def __unicode__(self):
        return self.name

    def action_approve(self, reviewer=None):
        """
        This method change the status of the MUOContainer object to 'approved' and it creates the
        relationship between the misuse case and all the use cases of the muo container.This change
        is allowed only if the current status is 'in_review'. If the current status is not
        'in_review', it raises the ValueError with appropriate message.
        :param reviewer: User object that approved the MUO
        :raise ValueError: if status not in 'in-review'
        """
        if self.status == 'in_review':
            # Create the relationship between the misuse case of the muo container with all the
            # use cases of the container
            for usecase in self.usecase_set.all():
                usecase.misuse_case = self.misuse_case
                usecase.save()

            self.status = 'approved'
            self.reviewed_by = reviewer
            self.save()
            # Send email
            muo_accepted.send(sender=self, instance=self)
        else:
            raise ValueError("In order to approve an MUO, it should be in 'in-review' state")

    def action_reject(self, reject_reason, reviewer=None):
        """
        This method change the status of the MUOContainer object to 'rejected' and the removes
        the relationship between all the use cases of the muo container and the misuse case.
        This change is allowed only if the current status is 'in_review' or 'approved'.
        If the current status is not 'in-review' or 'approved', it raises the ValueError
        with appropriate message.
        :param reject_reason: Message that contain the rejection reason provided by the reviewer
        :param reviewer: User object that approved the MUO
        :raise ValueError: if status not in 'in-review'
        """
        if self.status == 'in_review' or self.status == 'approved':
            # Remove the relationship between the misuse case of the muo container with all the
            # use cases of the container
            for usecase in self.usecase_set.all():
                usecase.misuse_case = None
                usecase.save()

            self.status = 'rejected'
            self.reject_reason = reject_reason
            self.reviewed_by = reviewer
            self.save()
            # Send email
            muo_rejected.send(sender=self, instance=self)
        else:
            raise ValueError("In order to approve an MUO, it should be in 'in-review' state")

    def action_submit(self):
        # This method change the status of the MUOContainer object to 'in_review'. This change
        # is allowed only if the current status is 'draft'. If the current status is not
        # 'draft', it raises the ValueError with appropriate message.
        if self.status == 'draft':
            if (self.usecase_set.count() == 0):
                raise ValidationError('A MUO Container must have at least one use case')

            self.status = 'in_review'
            self.save()
            # Send email
            muo_submitted_for_review.send(sender=self, instance=self)
        else:
            raise ValueError("You can only submit MUO for review if it is 'draft' state")

    def action_save_in_draft(self):
        # This method change the status of the MUOContainer object to 'draft'. This change
        # is allowed only if the current status is 'rejected' or 'in_review'. If the current
        # status is not 'rejected' or 'in_review', it raises the ValueError with
        # appropriate message.
        if self.status == 'rejected' or self.status == 'in_review':
            self.status = 'draft'
            self.save()
        else:
            raise ValueError("MUO can only be moved back to draft state if it is either rejected or 'in-review' state")

    def action_promote(self, reviewer=None):
        '''
        This method change the status of the custom MUO the from 'draft' to 'approved'. If the MUO is not
        custom or the state is not 'draft', it raises the ValueError with the appropriate message.
        :param reviewer: User object that has promoted the MUO
        :return: Null
        '''
        if self.is_custom == True and self.status == 'draft':
            self.status = 'approved'
            self.reviewed_by = reviewer
            self.save()
        else:
            raise ValueError("MUO can only be promoted if it is in draft state and custom.")


@receiver(post_save, sender=MUOContainer, dispatch_uid='muo_container_post_save_signal')
def post_save_muo_container(sender, instance, created, using, **kwargs):
    """ Set the value of the field 'name' after creating the object """
    if created:
        instance.name = "MUO/{0:05d}".format(instance.id)
        instance.save()



# TODO: This method is commented now because we need to take care of multiple deletion cases once the muo container is implemented
# @receiver(pre_delete, sender=MUOContainer, dispatch_uid='muo_container_delete_signal')
# def pre_delete_muo_container(sender, instance, using, **kwargs):
#     """
#     Pre-delete checks for MUO container
#     """
#     if instance.status not in ('draft', 'rejected'):
#         raise ValidationError(_('The %(name)s "%(obj)s" can only be deleted if in draft of rejected state') % {
#                                     'name': force_text(instance._meta.verbose_name),
#                                     'obj': force_text(instance.name),
#                                 })
#     elif instance.usecase_set.count() == 1:
#         # what if this muo container contains more than 1 use case?
#         instance.usecase_set.delete()
#     else:
#         raise ValidationError(_('The %(name)s "%(obj)s" can only be deleted because there are other use cases referring to it!') % {
#                                     'name': force_text(instance._meta.verbose_name),
#                                     'obj': force_text(instance.name),
#                                 })


class UseCase(BaseModel):
    name = models.CharField(max_length=16, null=True, blank=True, db_index=True, default="/")
    description = models.TextField()
    osr = models.TextField()
    misuse_case = models.ForeignKey(MisuseCase, null=True, blank=True)
    muo_container = models.ForeignKey(MUOContainer)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = "Use Case"
        verbose_name_plural = "Use Cases"

    def __unicode__(self):
        return "%s - %s..." % (self.name, self.description[:70])


    def get_absolute_url(self, language=None):
        content_type = ContentType.objects.get_for_model(MisuseCase)
        url = urlresolvers.reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model))
        return "%s?mu=%s&uc=%s" % (url, self.misuse_case.id, self.id)


@receiver(post_save, sender=UseCase, dispatch_uid='usecase_post_save_signal')
def post_save_usecase(sender, instance, created, using, **kwargs):
    """ Set the value of the field 'name' after creating the object """
    if created:
        instance.name = "UC/{0:05d}".format(instance.id)
        instance.save()



class IssueReport(BaseModel):
    name = models.CharField(max_length=16, null=True, blank=True, db_index=True, default="/")
    description = models.TextField(null=True, blank=True)
    type = models.CharField(choices=ISSUE_TYPES, max_length=64)
    status = models.CharField(choices=ISSUE_STATUS, max_length=64, default='open')
    usecase = models.ForeignKey(UseCase, on_delete=models.CASCADE, related_name='issue_reports')
    usecase_duplicate = models.ForeignKey(UseCase, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Issue Report"
        verbose_name_plural = "Issue Reports"

    def __unicode__(self):
        return self.name


@receiver(post_save, sender=IssueReport, dispatch_uid='issue_report_post_save_signal')
def post_save_issue_report(sender, instance, created, using, **kwargs):
    """ Set the value of the field 'name' after creating the object """
    if created:
        instance.name = "Issue/{0:05d}".format(instance.id)
        instance.save()
