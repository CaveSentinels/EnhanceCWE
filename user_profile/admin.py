from django.contrib import admin
from base.admin import BaseAdmin, admin_site
from models import *


@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(BaseAdmin):
    fields = ['user',
              'notify_muo_accepted',
              'notify_muo_rejected',
              'notify_muo_voted_up',
              'notify_muo_voted_down',
              'notify_muo_commented',
              'notify_muo_duplicate',
              'notify_muo_inappropriate',
              'notify_muo_submitted_for_review',
              'notify_custom_muo_created',
              'notify_custom_muo_promoted_as_generic']

