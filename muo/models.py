from django.core.exceptions import ValidationError
from django.db import models
from cwe.models import CWE
from base.models import BaseModel
from django.db import IntegrityError
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.db.models.signals import pre_delete
from django.dispatch import receiver

STATUS = [('draft', 'Draft'), ('in_review', 'In Review'), ('approved', 'Approved'), ('rejected', 'Rejected')]
PUBLISHED_STATUS = [('published', 'Published'), ('unpublished', 'Unpublished')]


class Tag(BaseModel):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __unicode__(self):
        return self.name


class MisuseCase(BaseModel):
    description = models.TextField()
    cwes = models.ManyToManyField(CWE, related_name='misuse_cases')
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = "Misuse Case"
        verbose_name_plural = "Misuse Cases"

    def __unicode__(self):
        return self.description[:100] + "..."

@receiver(pre_delete, sender=MisuseCase, dispatch_uid='misusecase_delete_signal')
def pre_delete_misusecase(sender, instance, using, **kwargs):
    """
    Prevent Misuse Case deletion if use cases are referring to it
    """
    if instance.use_cases.exists():
        raise IntegrityError(
            _('The %(name)s "%(obj)s" cannot be deleted as there are use cases referring to it!') % {
                'name': force_text(instance._meta.verbose_name),
                'obj': force_text(instance.__unicode__()),
            })


class UseCase(BaseModel):
    description = models.TextField()
    misuse_case = models.ForeignKey(MisuseCase, on_delete='Cascade', related_name='use_cases')
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = "Use Case"
        verbose_name_plural = "Use Cases"

    def __unicode__(self):
        return self.description[:100] + "..."

@receiver(pre_delete, sender=UseCase, dispatch_uid='usecase_delete_signal')
def pre_delete_usecase(sender, instance, using, **kwargs):
    """
    Prevent Use Case deletion if OSRs are referring to it
    """
    if instance.osrs.exists():
        raise IntegrityError(
            _('The %(name)s "%(obj)s" cannot be deleted as there are overlooked security requirements ' +
              'referring to it!') % {
                'name': force_text(instance._meta.verbose_name),
                'obj': force_text(instance.__unicode__()),
            })


class OSR(BaseModel):
    description = models.TextField()
    use_case = models.ForeignKey(UseCase, on_delete='Cascade', related_name='osrs')
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = "Overlooked Security Requirement"
        verbose_name_plural = "Overlooked Security Requirements"

    def __unicode__(self):
        return self.description[:100] + "..."


class MUOContainer(BaseModel):
    cwes = models.ManyToManyField(CWE, related_name='muo_container')
    misuse_cases = models.ManyToManyField(MisuseCase, related_name='muo_container')
    use_cases = models.ManyToManyField(UseCase, related_name='muo_container')
    osrs = models.ManyToManyField(OSR, related_name='muo_container')
    status = models.CharField(choices=STATUS, max_length=64, default='draft')
    published_status = models.CharField(choices=PUBLISHED_STATUS, max_length=32, default='unpublished')

    def action_approve(self):
        # This method change the status of the MUOContainer object to 'approved' and
        # published_status to 'published'. This change is allowed only if the current
        # status is 'in_review'. If the current status is not 'in-review', it raises
        # the ValueError with appropriate message.
        if self.status == 'in_review':
            self.status = 'approved'
            self.published_status = 'published'
            self.save()
        else:
            raise ValueError("In order to approve an MUO, it should be in 'in-review' state")

    def action_reject(self):
        # This method change the status of the MUOContainer object to 'rejected'.
        # This change is allowed only if the current status is 'in_review' or 'approved'.
        # If the current status is not 'in-review' or 'approved', it raises the ValueError
        # with appropriate message.
        if self.status == 'in_review' or self.status == 'approved':
            self.status = 'rejected'
            self.save()
        else:
            raise ValueError("In order to approve an MUO, it should be in 'in-review' state")

    def action_submit(self):
        # This method change the status of the MUOContainer object to 'in_review'. This change
        # is allowed only if the current status is 'draft'. If the current status is not
        # 'draft', it raises the ValueError with appropriate message.
        if self.status == 'draft':
            self.status = 'in_review'
            self.save()
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

    def action_publish(self):
        # This method change the published_status of the MUOContainer object to 'published'.
        # This change is allowed only if the current published_status is 'unpublished' and
        # status is 'approved'. If these two conditions are not met, it raises the ValueError
        # with appropriate message.
        if self.published_status == 'unpublished' and self.status == 'approved':
            self.published_status = 'published'
            self.save()
        else:
            raise ValueError("You can explicitly publish MUO only if it is approved and unpublished")

    def action_unpublish(self):
        # This method change the published_status of the MUOContainer object to 'unpublished'.
        # This change is allowed only if the current published_status is 'published'.
        # If these two conditions are not met, it raises the ValueError with appropriate message.
        if self.published_status == 'published':
            self.published_status = 'unpublished'
            self.save()
        else:
            raise ValueError("You can explicitly unpublish MUO only if it is published")

    class Meta:
        verbose_name = "MUO Container"
        verbose_name_plural = "MUO Containers"

@receiver(pre_delete, sender=MUOContainer, dispatch_uid='muo_container_delete_signal')
def pre_delete_muo_container(sender, instance, using, **kwargs):
    """
    Pre-delete checks for MUO container
    """
    if instance.state not in ('draft', 'rejected'):
        raise ValidationError(_('The %(name)s "%(obj)s" can only be deleted if in draft of rejected state') % {
                                    'name': force_text(instance._meta.verbose_name),
                                    'obj': force_text(instance.__unicode__()),
                                })

    # delete osrs, use cases and misuse cases if they are not pointed at by other containers
    if instance.osrs.muo_container.count() == 1:
        instance.osrs.delete()

    if instance.use_cases.muo_container.count() == 1:
        instance.use_cases.delete()

    if instance.misuse_cases.muo_container.count() == 1:
        instance.misuse_cases.delete()