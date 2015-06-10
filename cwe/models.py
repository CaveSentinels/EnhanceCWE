from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError
from base.models import BaseModel
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Category(BaseModel):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        # override default permissions to add 'view' permission that give readonly access rights
        default_permissions = ('add', 'change', 'delete', 'view')

    def __unicode__(self):
        return self.name


@receiver(pre_delete, sender=Category, dispatch_uid='category_delete_signal')
def pre_delete_category(sender, instance, using, **kwargs):
    """
    Prevent Category deletion if CWEs are referring to it
    """
    if instance.cwes.exists():
        raise IntegrityError(
            _('The %(name)s "%(obj)s" cannot be deleted as there are CWEs referring to it!') % {
                'name': force_text(instance._meta.verbose_name),
                'obj': force_text(instance.__unicode__()),
            })


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
        # override default permissions to add 'view' permission that give readonly access rights
        default_permissions = ('add', 'change', 'delete', 'view')

    def __unicode__(self):
        return "CWE-%s: %s" % (self.code, self.name)

@receiver(pre_delete, sender=CWE, dispatch_uid='cwe_delete_signal')
def pre_delete_cwe(sender, instance, using, **kwargs):
    """
    Prevent CWE deletion if misuse cases are referring to it
    """
    if instance.misuse_cases.exists():
        raise IntegrityError(
            _('The %(name)s "%(obj)s" cannot be deleted as there are misuse cases referring to it!') % {
                'name': force_text(instance._meta.verbose_name),
                'obj': force_text(instance.__unicode__()),
            })