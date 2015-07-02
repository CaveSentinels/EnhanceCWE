from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import (
    quote, )
from django.http import HttpResponseRedirect
from django.template.response import SimpleTemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape, escapejs
from django.utils.translation import ugettext as _
from django.utils.crypto import get_random_string
from django.core.urlresolvers import reverse
from allauth.utils import build_absolute_uri
from allauth.account import app_settings

from models import *
from base.admin import BaseAdmin


IS_POPUP_VAR = '_popup'
TO_FIELD_VAR = '_to_field'


# Register your models here.
@admin.register(EmailInvitation)
class EmailInvitationAdmin(BaseAdmin):
    fields = ['email_address']


    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        msg_dict = {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.

        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)
            if to_field:
                attr = str(to_field)
            else:
                attr = obj._meta.pk.attname
            value = obj.serializable_value(attr)
            return SimpleTemplateResponse('admin/popup_response.html', {
                'pk_value': escape(pk_value),  # for possible backwards-compatibility
                'value': escape(value),
                'obj': escapejs(obj)
            })

        elif "_continue" in request.POST:
            msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % msg_dict
            self.message_user(request, msg, messages.SUCCESS)
            if post_url_continue is None:
                post_url_continue = reverse('admin:%s_%s_change' %
                                            (opts.app_label, opts.model_name),
                                            args=(quote(pk_value),),
                                            current_app=self.admin_site.name)
            post_url_continue = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url_continue
            )
            return HttpResponseRedirect(post_url_continue)

        elif "_addanother" in request.POST:
            msg = _('The %(name)s "%(obj)s" was added successfully. You may add another %(name)s below.') % msg_dict
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            email_add = request.POST['email_address']

            random_key = obj.key
            activate_url = '/accounts/signup?token='+ random_key + '&email='+email_add
            activate_url = build_absolute_uri(request, activate_url, protocol=app_settings.DEFAULT_HTTP_PROTOCOL)


            message_body = 'The EnhancedCWE Application admin has sent an invitation to join. Please click the following URL to sign the registration process \n' + activate_url

            from django.core.mail import EmailMessage
            email = EmailMessage('Enhanced CWE Invite', message_body, to=[email_add])
            email.send()

            msg = _('The email invitation was sent successfully to ' + email_add)
            self.message_user(request, msg, messages.SUCCESS)
            return self.response_post_save_add(request, obj)








