from django.contrib.auth.models import Group, User
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from .settings import SET_STAFF_ON_REGISTRATION

# Make user email field required
User._meta.get_field('email').null = False
User._meta.get_field('email').blank = False


# Adds a boolean field 'is_auto_assign_contributor' to the group
if not hasattr(Group, 'is_auto_assign_contributor'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign Contributor'))
    field.contribute_to_class(Group, 'is_auto_assign_contributor')

# Adds a boolean field 'is_auto_assign_client' to the group
if not hasattr(Group, 'is_auto_assign_client'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign Client'))
    field.contribute_to_class(Group, 'is_auto_assign_client')



class CustomUserModel(models.Model):
    """
    This model holds extra information about the user. In this case, it holds the information if he intends to
    register as a contributor or the client. This information will be used to auto assign him to the default groups
    """
    user = models.OneToOneField(User)
    role = models.CharField(max_length=20, choices=[(1, 'Contributor'), (2, 'Client')], default='2')


@receiver(post_save, sender=CustomUserModel, dispatch_uid='add_user_to_default_groups')
def add_group_to_user1(sender, instance, created, using, **kwargs):
    """
    This method adds users after saving them to default groups as defined by 'is_auto_assign_contributor' and
    'is_auto_assign_client'
    """
    if created:
        user = instance.user

        # Filter all those groups with assignable attribute set to True
        if instance.role == 'Contributor':
            groups = list(Group.objects.filter(is_auto_assign_contributor=True))
            user.groups.add(*groups)

        elif instance.role == 'Client':
            groups = list(Group.objects.filter(is_auto_assign_client=True))
            user.groups.add(*groups)


        if SET_STAFF_ON_REGISTRATION:
            user.is_staff = True
            user.save()
