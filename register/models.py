from django.contrib.auth.models import Group, User
from django.db import models
from registration.signals import user_registered
from registration import forms
from django.utils.translation import ugettext_lazy as _


Group.add_to_class('if_assignable', models.BooleanField(default=False))


from django.dispatch import receiver
@receiver(user_registered, dispatch_uid="user_accepted_id")
def include_in_group(sender, **kwargs):
    # kwargs contains a dictionary of
    # 1. profile, 2. request, 3. signal, 4. user (userid)
    registered_user_id = kwargs["user"].username
    user_in_db = User.objects.filter(username=registered_user_id)
    user_id = user_in_db[0].id

    group_list = Group.objects.filter(if_assignable=True)
    for group in group_list:
        group.user_set.add(user_id)

    print 'User added to group'


