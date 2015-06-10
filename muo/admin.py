from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from models import *

from django.http import HttpResponseRedirect
from base.admin import BaseAdmin


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(OSR)
class OSRAdmin(BaseAdmin):
    fields = ['name', 'description', 'use_case', 'tags']
    readonly_fields = ['name']
    list_display = ['name']
    search_fields = ['name', 'description', 'tags__name']


class OSRAdminInline(admin.TabularInline):
    model = OSR
    extra = 1
    fields = ['name', 'description', 'tags']
    readonly_fields = ['name']


@admin.register(UseCase)
class UseCaseAdmin(BaseAdmin):
    fields = ['name', 'misuse_case', 'description', 'tags']
    readonly_fields = ['name']
    list_display = ['name']
    search_fields = ['name', 'description', 'tags__name']
    inlines = [OSRAdminInline]



class UseCaseAdminInLine(admin.StackedInline):
    model = UseCase
    extra = 1
    fields = ['name', 'description', 'tags']
    readonly_fields = ['name']


@admin.register(MisuseCase)
class MisuseCaseAdmin(BaseAdmin):
    fields = ['name', 'cwes', ('description', 'tags')]
    readonly_fields = ['name']
    list_display = ['name']
    search_fields = ['name', 'description', 'tags__name']
    inlines = [UseCaseAdminInLine]


@admin.register(MUOContainer)
class MUOContainerAdmin(BaseAdmin):
    list_display = ['name', 'status', 'published_status']
    readonly_fields = ['name', 'status', 'published_status']
    exclude = ['created_at', 'modified_at', 'created_by', 'modified_by']
    search_fields = ['name', 'status']
    date_hierarchy = 'created_at'

    # Override response_change method of admin/options.py to handle the click of
    # newly added buttons
    def response_change(self, request, obj, *args, **kwargs):
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
            if "_approve" in request.POST:
                obj.action_approve()
                msg = "You have approved the submission and it is now published"
            elif "_reject" in request.POST:
                obj.action_reject()
                msg = "The submission has been sent back to the author for review"
            elif "_submit_for_review" in request.POST:
                obj.action_submit()
                msg = "Your review request has been successfully submitted"
            elif "_edit" in request.POST:
                obj.action_save_in_draft()
                msg = "You can now edit the MUO"
            elif "_publish" in request.POST:
                obj.action_publish()
                msg = "MUO has been successfully published"
            elif "_unpublish" in request.POST:
                obj.action_unpublish()
                msg = "You have unpublished this MUO"
            else:
                # Let super class 'ModelAdmin' handle rest of the button clicks i.e. 'save' 'save and continue' etc.
                return super(MUOContainerAdmin, self).response_change(request, obj, *args, **kwargs)
        except ValueError as e:
            # In case the state of the object is not suitable for the corresponding action,
            # model will raise the value exception with the appropriate message. Catch the
            # exception and show the error message to the user
            msg = e.message
            self.message_user(request, msg, messages.ERROR)
            return HttpResponseRedirect(redirect_url)

        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)
