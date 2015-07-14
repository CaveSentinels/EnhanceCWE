from django.contrib import admin
from allauth.account.models import EmailAddress
from base.admin import BaseAdmin
from register_approval.admin import EmailAddressAdmin


class ClientEmailAddressAdmin(EmailAddressAdmin):
    list_display = ('email', 'user', 'primary', 'verified', 'admin_approval', 'requested_role')
    list_filter = ('primary', 'verified', 'admin_approval', 'requested_role')

    fields = [('user', 'admin_approval'), 'email', ('primary', 'verified'), 'created_at', ('modified_at', 'modified_by'), 'requested_role']
    readonly_fields = ['admin_approval', 'created_at', 'modified_by', 'modified_at']
    raw_id_fields = ('user',)

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, ClientEmailAddressAdmin)