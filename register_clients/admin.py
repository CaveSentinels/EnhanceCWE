from django.contrib import admin
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from base.admin import BaseAdmin


class EmailAddressAdmin(BaseAdmin):
    list_display = ('email', 'user', 'primary', 'verified', 'requested_role')
    list_filter = ('primary', 'verified', 'requested_role')
    search_fields = ['']
    # fields = [('user', 'admin_approval'), 'email', ('primary', 'verified'), 'created_at', ('modified_at', 'modified_by')]
    # readonly_fields = ['admin_approval', 'created_at', 'modified_by', 'modified_at']
    # raw_id_fields = ('user',)

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)