from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from register_approval.signals import register_approved, register_rejected


@receiver(register_approved)
def create_auth_token(sender, instance, **kwargs):
    """
    Create the token once the user is approved.
    """
    if getattr(instance, 'requested_role', None) == 'client':
        Token.objects.create(user=instance.user)


@receiver(register_rejected)
def delete_auth_token(sender, instance, **kwargs):
    """
    delete the token once the user is rejected.
    """
    Token.objects.filter(user=instance.user).delete()