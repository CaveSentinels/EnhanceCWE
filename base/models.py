from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BaseModel(models.Model):
    """
    This is a base abstract model that provides basic common features that are
    necessary to most models.
    Interested models should inherit from this class instead of models.Model
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, related_name='+')
    modified_by = models.ForeignKey(User, null=True, related_name='+')
    active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

