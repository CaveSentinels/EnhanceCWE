from django.contrib.auth.models import Group, User
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from .settings import SET_STAFF_ON_REGISTRATION
from allauth.account.models import EmailAddress

# Adds a boolean field 'is_auto_assign_client' to the Groups
if not hasattr(Group, 'is_auto_assign_client'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign to Clients'))
    field.contribute_to_class(Group, 'is_auto_assign_client')

# Adds a boolean field 'is_auto_assign_contributors' to the Groups
if not hasattr(Group, 'is_auto_assign_contributors'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign to Contributors'))
    field.contribute_to_class(Group, 'is_auto_assign_contributors')

# Adds a boolean field 'requested_role' to the EmailAddress
if not hasattr(EmailAddress, 'requested_role'):
    field = models.CharField(max_length=20, choices=[('contributor', 'Contributor'), ('client', 'Client')])
    field.contribute_to_class(EmailAddress, 'requested_role')



@receiver(post_save, sender=EmailAddress, dispatch_uid='add_user_to_default_groups')
def add_client_group_to_user(sender, instance, created, using, **kwargs):
    """
    This method adds users after saving them to default groups as defined by 'is_auto_assign_contributor' and
    'is_auto_assign_client'
    """
    if created:
        user = instance.user
        email = EmailAddress.objects.filter(user_id=user.id)
        requested_role = email[0].requested_role

        # Filter all those groups with assignable attribute set to True
        if requested_role == 'Client':
            groups = list(Group.objects.filter(is_auto_assign_client=True))
            user.groups.add(*groups)

        # Filter all those groups with assignable attribute set to True
        if requested_role == 'Contributor':
            groups = list(Group.objects.filter(is_auto_assign_contributors=True))
            user.groups.add(*groups)

        if SET_STAFF_ON_REGISTRATION:
            user.is_staff = True
            user.save()