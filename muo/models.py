from django.db import models

from cwe.models import CWE
from cwe.models import BaseModel


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