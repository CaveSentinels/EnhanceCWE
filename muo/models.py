from django.db import models
from cwe.models import CWE
from base.models import BaseModel


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


class UseCase(BaseModel):
    description = models.TextField()
    misuse_case = models.ForeignKey(MisuseCase, on_delete='Cascade', related_name='use_cases')
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = "Use Case"
        verbose_name_plural = "Use Cases"

    def __unicode__(self):
        return self.description[:100] + "..."


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
    cwes = models.ManyToManyField(CWE)
    misuse_cases = models.ManyToManyField(MisuseCase)
    use_cases = models.ManyToManyField(UseCase)
    osrs = models.ManyToManyField(OSR)
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