from django.contrib.auth.models import Group, User
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from allauth.account.signals import email_confirmed
from . import settings

# Make user email field required
User._meta.get_field('email').null = False
User._meta.get_field('email').blank = False


# Adds a boolean field 'is_auto_assign' to the group
if not hasattr(Group, 'is_auto_assign'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign:'))
    field.contribute_to_class(Group, 'is_auto_assign')


@receiver(email_confirmed, dispatch_uid="email_confirmed")
def add_group_to_user(sender, email_address, **kwargs):
    """
    This method listens to a signal "user_registered" and adds him to the groups which are assignable.
    :param: sender and argument array
    :param: email address object that has been confirmed
    :return: null
    """

    # Get the user object which is sent from the form
    user = email_address.user

    # Filter all those groups with assignable attribute set to True
    groups = list(Group.objects.filter(is_auto_assign=True))
    user.groups.add(*groups)

    if getattr(settings, 'SET_STAFF_ON_REGISTRATION', False):
        user.is_staff = True
        user.save()


