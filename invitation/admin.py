from django.contrib import admin
from django.core.checks import messages
from base.admin import BaseAdmin
from models import *
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect
from base.admin import BaseAdmin
from django.core.exceptions import ValidationError


# Register your models here.
@admin.register(EmailInvitation)
class EmailInvitationAdmin(BaseAdmin):
    fields = ['email_address']

def response_change(self, request, obj, *args, **kwargs):
        '''
        Override response_change method of admin/options.py to handle the click of
        newly added buttons
        '''

        # Get the metadata about self (it tells you app and current model)
        opts = self.model._meta

        # Get the primary key of the model object i.e. MUO Container
        pk_value = obj._get_pk_val()

        preserved_filters = self.get_preserved_filters(request)

        redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(pk_value,))
        redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

        # Check which button is clicked, handle accordingly.
        try:
            if "_sendinvitation" in request.POST:
                obj.send_invitation(request)
                msg = "An email invitation has been sent"

            else:
                # Let super class 'ModelAdmin' handle rest of the button clicks i.e. 'save' 'save and continue' etc.
                return super(EmailInvitationAdmin, self).response_change(request, obj, *args, **kwargs)
        except ValueError as e:
            # In case the state of the object is not suitable for the corresponding action,
            # model will raise the value exception with the appropriate message. Catch the
            # exception and show the error message to the user
            msg = e.message
            self.message_user(request, msg, messages.ERROR)
            return HttpResponseRedirect(redirect_url)
        except ValidationError as e:
            # If incomplete MUO Container is attempted to be approved or submitted for review, a validation error will
            # be raised with an appropriate message
            msg = e.message
            self.message_user(request, msg, messages.ERROR)
            return HttpResponseRedirect(redirect_url)

        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)
