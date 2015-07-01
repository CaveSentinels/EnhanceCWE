from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name="profile")
    notify_muo_accepted = models.BooleanField(default=True)
    notify_muo_rejected = models.BooleanField(default=True)
    notify_muo_voted_up = models.BooleanField(default=True)
    notify_muo_voted_down = models.BooleanField(default=True)
    notify_muo_commented = models.BooleanField(default=True)
    notify_muo_duplicate = models.BooleanField(default=True)
    notify_muo_inappropriate = models.BooleanField(default=True)
    notify_muo_submitted_for_review = models.BooleanField(default=True)
    notify_custom_muo_created = models.BooleanField(default=True)
    notify_custom_muo_promoted_as_generic = models.BooleanField(default=True)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])





