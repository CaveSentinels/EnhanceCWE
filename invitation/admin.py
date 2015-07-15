from django.contrib import admin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from models import *
from base.admin import BaseAdmin


# Register your models here.
@admin.register(EmailInvitation)
class EmailInvitationAdmin(BaseAdmin):
    fields = ['email', ('key', 'status'), ('created_by', 'created_at')]
    readonly_fields = ['key', 'status', 'created_by', 'created_at']
    list_display = ['email', 'created_by', 'created_at', 'status']
    search_fields = ['email', 'created_at']
    list_filter = ['created_at', 'status']
    date_hierarchy = 'created_at'


    def response_change(self, request, obj, *args, **kwargs):
        """
        Override response_change method of admin/options.py to send invitation on save
        """

        # Check which button is clicked, handle accordingly.
        if "_invite" in request.POST:
            obj.send_invitation()

        # Let super class 'ModelAdmin' handle rest of the button clicks
        return super(EmailInvitationAdmin, self).response_change(request, obj, *args, **kwargs)
