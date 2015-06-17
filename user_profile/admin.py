from django.contrib import admin
from base.admin import BaseAdmin, admin_site
from models import *


@admin.register(MUONotification, site=admin_site)
class MUONotificationAdmin(BaseAdmin):
    fields = ['notify_when_muo_accepted','notify_when_muo_rejected','notify_when_muo_voted_up',
              'notify_when_muo_voted_down','notify_when_muo_commented',
              'notify_when_muo_duplicate','notify_when_muo_inappropriate','notify_when_muo_submitted_for_review',
              'notify_when_custom_muo_created','notify_when_custom_muo_promoted_as_generic']

