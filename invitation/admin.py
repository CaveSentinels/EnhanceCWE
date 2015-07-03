from django.contrib import admin
from models import *
from base.admin import BaseAdmin

# Register your models here.
@admin.register(EmailInvitation)
class EmailInvitationAdmin(BaseAdmin):
    fields = ['email', 'key', ('created_by', 'created_at')]
    readonly_fields = ['key', 'created_by', 'created_at']
    list_display = ['email', 'created_by', 'created_at']
    search_fields = ['email', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
