from django.db import models
from cwe.models import CWE
from cwe.models import BaseModel


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

    class Meta:
        verbose_name = "MUO Container"
        verbose_name_plural = "MUO Containers"
