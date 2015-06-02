from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BaseModel(models.Model):

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='+')
    modified_by = models.ForeignKey(User, related_name='+')

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name


class Keyword(BaseModel):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"

    def __unicode__(self):
        return self.name

class CWE(BaseModel):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='cwes')
    keywords = models.ManyToManyField(Keyword, related_name='cwes', blank=True)

    class Meta:
        verbose_name = "CWE"
        verbose_name_plural = "CWEs"

    def __unicode__(self):
        return "CWE-%s: %s" % (self.code, self.name)
