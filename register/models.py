from django.contrib.auth.models import Group, User
from django.db import models
from registration.signals import user_registered
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

# Adds a boolean field 'if_assignable' to the group
Group.add_to_class('is_auto_assign', models.BooleanField(default=False, verbose_name=_('Auto Assign:')))


@receiver(user_registered, dispatch_uid="user_accepted_id")
def add_group_to_user(sender, **kwargs):
    """
    This method listens to a signal "user_registered" and adds him to the groups which are assignable.
    :param: sender and argument array
    :return: null
    """

    # Get the user object which is sent from the form
    user = kwargs["user"]

    # Filter all those groups with assignable attribute set to True
    group_list = Group.objects.filter(is_auto_assign=True)

    # Iterate over the list and add these groups to the user
    for group in group_list:
        user.groups.add(group.id)