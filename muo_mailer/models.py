from django.conf import settings
from django.contrib.auth.models import  User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class MailerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name="mailer_profile")
    notify_muo_accepted = models.BooleanField(default=True, verbose_name='When My MUO is Accepted')
    notify_muo_rejected = models.BooleanField(default=True, verbose_name='When My MUO is Rejected')
    notify_muo_commented = models.BooleanField(default=True, verbose_name='When My MUO is Commented On')
    notify_muo_inappropriate = models.BooleanField(default=True, verbose_name='When an MUO is Reported Inappropriate')
    notify_muo_submitted_for_review = models.BooleanField(default=True, verbose_name='When an MUO is Submitted for Review')
    notify_custom_muo_created = models.BooleanField(default=True, verbose_name='When a Custom MUO is Created')
    notify_custom_muo_promoted_as_generic = models.BooleanField(default=True, verbose_name='When a Custom MUO is Promoted')


    def __unicode__(self):
        return self.user.username

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            MailerProfile.objects.get_or_create(user=instance)

    @receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
    def delete_profile_for_user(sender, instance=None, **kwargs):
        if instance:
            user_profile = MailerProfile.objects.get(user=instance)
            user_profile.delete()

User.mailer_profile = property(lambda u: MailerProfile.objects.get_or_create(user=u)[0])



