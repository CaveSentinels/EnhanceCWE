from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models, transaction
from django.conf import settings
from cwe.models import CWE
from base.models import BaseModel
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, pre_delete, post_save
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
                ('reopened','Re-opened'),
                 ('resolved', 'Resolved')]


class Tag(BaseModel):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        default_permissions = ('add', 'change', 'delete', 'view')

    def __unicode__(self):
        return self.name


class MUOQuerySet(models.QuerySet):
    """
    Define custom methods for the MUO QuerySet
    """

    def approved(self):
        # Returns the queryset for all the approved MUO Containers
        if self.model == MUOContainer:
            return self.filter(status='approved')
        elif self.model == MisuseCase:
            return self.filter(muocontainer__status='approved')
        elif self.model == UseCase:
            return self.filter(muo_container__status='approved')

    def rejected(self):
        # Returns the queryset for all the rejected MUO Containers
        if self.model == MUOContainer:
            return self.filter(status='rejected')
        elif self.model == MisuseCase:
            return self.filter(muocontainer__status='rejected')
        elif self.model == UseCase:
            return self.filter(muo_container__status='rejected')

    def draft(self):
        # Returns the queryset for all the draft MUO Containers
        if self.model == MUOContainer:
            return self.filter(status='draft')
        elif self.model == MisuseCase:
            return self.filter(muocontainer__status='draft')
        elif self.model == UseCase:
            return self.filter(muo_container__status='draft')

    def in_review(self):
        # Returns the queryset for all the in review MUO Containers
        if self.model == MUOContainer:
            return self.filter(status='in_review')
        elif self.model == MisuseCase:
            return self.filter(muocontainer__status='in_review')
        elif self.model == UseCase:
            return self.filter(muo_container__status='in_review')

    def custom(self):
        # Returns the queryset for all the custom MUO Containers
        if self.model == MUOContainer:
            return self.filter(is_custom=True)
        elif self.model == MisuseCase:
            return self.filter(muocontainer__is_custom=True)
        elif self.model == UseCase:
            return self.filter(muo_container__is_custom=True)


class MUOManager(models.Manager):
    """
    Define custom methods that can be called on the MUO Manager
    """

    def get_queryset(self):
        return MUOQuerySet(self.model, using=self._db)

    def approved(self):
        return self.get_queryset().approved()

    def draft(self):
        return self.get_queryset().draft()

    def rejected(self):
        return self.get_queryset().rejected()

    def in_review(self):
        return self.get_queryset().in_review()

    def custom(self):
        return self.get_queryset().custom()


class MisuseCase(BaseModel):
    name = models.CharField(max_length=16, null=True, blank=True, db_index=True, default="/")
    description = models.TextField()
    cwes = models.ManyToManyField(CWE, related_name='misuse_cases')
    tags = models.ManyToManyField(Tag, blank=True)

    objects = MUOManager()  # Replace the default manager with the MUOManager

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
    misuse_case = models.ForeignKey(MisuseCase, on_delete=models.PROTECT, null=True, blank=True)
    new_misuse_case = models.TextField(null=True, blank=True)
    reject_reason = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=64, default='draft')
    is_custom = models.BooleanField(default=False, db_index=True)

    objects = MUOManager()  # Replace the default manager with the MUOManager

    class Meta:
        verbose_name = "MUO Container"
        verbose_name_plural = "MUO Containers"
        # additional permissions
        permissions = (
            ('can_approve', 'Can approve MUO container'),
            ('can_reject', 'Can reject MUO container'),
            ('can_edit_all', 'Can edit all MUO Containers'),
            ('can_view_all', 'Can view all MUO containers'),
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
        cwe_objects = list(CWE.objects.filter(code__in=cwe_ids))

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
        'in_review', it raises the ValueError with appropriate message. In case of a new misuse case
        is written, it also creates the MisuseCase object and then relate it to the CWEs and the
        MUOContainer.
        :param reviewer: User object that approved the MUO
        :raise ValueError: if status not in 'in-review'
        """
        if self.status == 'in_review':
            if self.misuse_case is None:
                # misuse_case is None that means the author has written a new misuse case.
                # A new misuse case object needs to be created and related with the current
                # MUOContainer and CWEs
                misuse_case = MisuseCase(description=self.new_misuse_case,
                                         created_by=self.created_by,
                                         created_at=self.created_at)
                misuse_case.save()
                misuse_case.cwes.add(*list(self.cwes.all()))
                self.misuse_case = misuse_case
                self.new_misuse_case = None  # Remove the text from the new_misuse_case

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


@receiver(pre_delete, sender=MUOContainer, dispatch_uid='muo_container_delete_signal')
def pre_delete_muo_container(sender, instance, using, **kwargs):
    """
    Registering for pre_delete signal, so that we can prevent deletion of MUOContainer if it is not in
    'draft' or 'review' state.
    """
    if instance.status not in ('draft', 'rejected'):
        raise ValidationError('The MUOContainer can only be deleted if in draft or rejected state')



@receiver(post_delete, sender=MUOContainer, dispatch_uid='muo_container_post_delete_signal')
def post_delete_muo_container(sender, instance, using, **kwargs):
    """
    Registering for the post_delete signal, so that after MUOContainer deletion, we can delete the related
    Misuse Case also if it is not related to any other MUOContainer
    """
    if instance.misuse_case is not None:
        if instance.misuse_case.muocontainer_set.count() == 0:
            instance.misuse_case.delete()


class UseCase(BaseModel):
    name = models.CharField(max_length=16, null=True, blank=True, db_index=True, default="/")
    description = models.TextField()
    osr = models.TextField()
    misuse_case = models.ForeignKey(MisuseCase, null=True, blank=True)
    muo_container = models.ForeignKey(MUOContainer)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = MUOManager()  # Replace the default manager with the MUOManager

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
    status = models.CharField(choices=ISSUE_STATUS, max_length=64, db_index=True, default='open')
    usecase = models.ForeignKey(UseCase, on_delete=models.CASCADE, related_name='issue_reports')
    usecase_duplicate = models.ForeignKey(UseCase, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True)
    resolve_reason = models.TextField(null=True, blank=True, default="/")

    class Meta:
        verbose_name = "Issue Report"
        verbose_name_plural = "Issue Reports"

    def __unicode__(self):
        return self.name

    def action_investigate(self, reviewer= None):
        """
        This method change the status of the issue report object to 'investigating' and This change
        is allowed only if the current status is either open or re open.
        """
        if self.status in ('open','reopened'):
            self.status = 'investigating'
            self.reviewed_at = timezone.now()
            self.reviewed_by = reviewer
            self.save()

        else:
            raise ValueError("In order to investigate a report, it should be in open or re-open state")

    def action_resolve(self, resolve_reason, reviewer= None):
        """
        This method change the status of the issue report object to 'resolved' and This change
        is allowed only if the current status is 'investigating'.
        """
        if self.status == 'investigating':
            self.status = 'resolved'
            # Get the current date when it got resolved
            # TODO: This has to be used in future
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.resolve_reason = resolve_reason
            self.save()
        else:
            raise ValueError("In order to resolve a report, it should be in investigating state")

    def action_reopen(self, reviewer=None):
        """
        This method change the status of the issue report object to 're open' and This change
        is allowed only if the current status is 'investigating' or 'resolved'.
        """
        if self.status == 'resolved':
            self.status = 'reopened'
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.save()
        else:
            raise ValueError("In order to re open an issue it should be in resolved state")

    def action_open(self,reviewer= None):
        """
        This method change the status of the issue report object to 'open' and This change
        is allowed only if the current status is 'investigating'.
        """
        if self.status == 'investigating':
            self.status = 'open'
            self.reviewed_at = timezone.now()
            self.reviewed_by = reviewer
            self.save()
        else:
            raise ValueError("In order to open an issue it should be in open state")


@receiver(post_save, sender=IssueReport, dispatch_uid='issue_report_post_save_signal')
def post_save_issue_report(sender, instance, created, using, **kwargs):
    """ Set the value of the field 'name' after creating the object """
    if created:
        instance.name = "Issue/{0:05d}".format(instance.id)
        instance.save()

