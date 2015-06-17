from django.conf import settings
from django.db import models

class MUONotification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    notify_when_muo_accepted = models.BooleanField(default=False)
    notify_when_muo_rejected = models.BooleanField(default=False)
    notify_when_muo_voted_up = models.BooleanField(default=False)
    notify_when_muo_voted_down = models.BooleanField(default=False)
    notify_when_muo_commented = models.BooleanField(default=False)
    notify_when_muo_duplicate = models.BooleanField(default=False)
    notify_when_muo_inappropriate = models.BooleanField(default=False)
    notify_when_muo_submitted_for_review = models.BooleanField(default=False)
    notify_when_custom_muo_created = models.BooleanField(default=False)
    notify_when_custom_muo_promoted_as_generic = models.BooleanField(default=False)








