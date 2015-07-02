from django.db import models
from django.dispatch import receiver
from django.utils.crypto import get_random_string

class EmailInvitation(models.Model):
    email_address = models.CharField(max_length=100)
    key = models.CharField(verbose_name='key', max_length=64, unique=True)


from django.db.models.signals import post_save, pre_save


@receiver(pre_save, sender=EmailInvitation, dispatch_uid='usecase_post_save_signal')
def update_key(sender, instance, *args, **kwargs):
    random_key = get_random_string(64).lower()
    instance.key = random_key
