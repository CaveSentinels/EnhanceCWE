from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError
from base.models import BaseModel
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _


class Category(BaseModel):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name

    def delete(self, using=None):
        if self.cwes.exists():
            raise IntegrityError(
                _('The %(name)s "%(obj)s" cannot be deleted as there are CWEs referring to it!') % {
                    'name': force_text(self._meta.verbose_name),
                    'obj': force_text(self.__unicode__()),
                })

        else:
            super(Category, self).delete(using)


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
