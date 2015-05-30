from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from models import *

from django.http import HttpResponseRedirect


class TagAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


class OSRAdmin(admin.ModelAdmin):
    fields = ['description', 'use_case', 'tags']
    search_fields = ['description', 'tags__name']


class OSRAdminInline(admin.TabularInline):
    model = OSR
    extra = 1
    fields = ['description', 'tags']


class UseCaseAdmin(admin.ModelAdmin):
    fields = ['misuse_case', 'description', 'tags']
    inlines = [OSRAdminInline]


class UseCaseAdminInLine(admin.TabularInline):
    model = UseCase
    extra = 1
    fields = ['description', 'tags']


class MisuseCaseAdmin(admin.ModelAdmin):
    fields = ['cwes', ('description', 'tags')]
    inlines = [UseCaseAdminInLine]


class MUOContainerAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'published_status')
    readonly_fields = ['status', 'published_status']
    exclude = ['created', 'modified']
    search_fields = ['status']


    def change_status(self, object, state, published_state):
        '''
        :param object: MUOContainer
        :param state: String
        :param published_state: String
        :return: void
        '''
        object.status = state
        object.published_status = published_state
        object.save()


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

        if "_approve" in request.POST:
            self.change_status(obj, 'approved', 'published')
            msg = "You have approved the submission and it is now published"
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(redirect_url)
        elif "_reject" in request.POST:
            self.change_status(obj, 'rejected', 'unpublished')
            msg = "The submission has been sent back to the author for review"
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(redirect_url)
        elif "_submit_for_review" in request.POST:
            self.change_status(obj, 'in_review', 'unpublished')
            msg = "Your review request has been successfully submitted"
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(redirect_url)
        elif "_edit" in request.POST:
            self.change_status(obj, 'draft', 'unpublished')
            msg = "Now you can edit"
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(redirect_url)
        elif "_publish" in request.POST:
            self.change_status(obj, 'approved', 'published')
            msg = "MUO has been successfully published"
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(redirect_url)
        elif "_unpublish" in request.POST:
            self.change_status(obj, 'approved', 'unpublished')
            msg = "You have unpublished this MUO"
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(redirect_url)
        else:
            # Let super class 'ModelAdmin' handle rest of the button clicks
            return super(MUOContainerAdmin, self).response_change(request, obj, *args, **kwargs)



admin.site.register(Tag, TagAdmin)
admin.site.register(MisuseCase, MisuseCaseAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(OSR, OSRAdmin)
admin.site.register(MUOContainer, MUOContainerAdmin)
