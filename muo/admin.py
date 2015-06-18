from django.db.models import Q
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.shortcuts import render
from django.http import Http404
from django.template.response import TemplateResponse
from django.conf.urls import url
import autocomplete_light
from models import *

from django.http import HttpResponseRedirect
from base.admin import BaseAdmin, admin_site


@admin.register(Tag, site=admin_site)
class TagAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(UseCase, site=admin_site)
class UseCaseAdmin(BaseAdmin):
    fields = ['name', 'misuse_case', 'description', 'osr', 'tags']
    readonly_fields = ['name']
    list_display = ['name']
    search_fields = ['name', 'description', 'tags__name']


class UseCaseAdminInLine(admin.StackedInline):
    model = UseCase
    extra = 0
    fields = ['name', 'description', 'osr']
    readonly_fields = ['name']


@admin.register(MisuseCase, site=admin_site)
class MisuseCaseAdmin(BaseAdmin):
    fields = ['name', 'cwes', ('description', 'tags')]
    readonly_fields = ['name']
    list_display = ['name']
    search_fields = ['name', 'description', 'tags__name']
    inlines = [UseCaseAdminInLine]

    def get_urls(self):
        #  Add the additional urls to the url list. These additional urls are for making ajax requests

        urls = super(MisuseCaseAdmin, self).get_urls()

        additional_urls = [
            url(r'^usecases/$', self.admin_site.admin_view(self.usecases_view)),
        ]

        return additional_urls + urls


    def usecases_view(self, request):
        if request.method != 'GET':
            raise Http404("Invalid access not using GET request!")

        misuse_case_id = request.GET['misuse_case_id']

        try:
            # Fetch the misuse case object for the misuse_case_id
            misuse_case = MisuseCase.objects.get(pk=misuse_case_id)
        except ObjectDoesNotExist as e:
            raise Http404("Misuse case with id %d doesn't exist", misuse_case_id)

        #  Create a context with all the corresponding use cases
        context = {'use_cases': misuse_case.usecase_set.all()}

        return TemplateResponse(request, "admin/muo/misusecase/usecase.html", context)


    def changelist_view(self, request, extra_context=None):
        if request.GET.get('_popup', False):
            #  If its a popup request let super handle it
            return super(MisuseCaseAdmin, self).changelist_view(request, extra_context)

        # Render the custom template for the changelist_view
        # TODO: Don't pass misuse cases and use cases here. Decide what will be shown the first time page is rendered
        misuse_cases = MisuseCase.objects.all()
        use_cases = UseCase.objects.all()

        context = {'misuse_cases': misuse_cases,
                   'use_cases': use_cases}

        return render(request, 'admin/muo/misusecase/misusecase_search.html', context)


@admin.register(MUOContainer, site=admin_site)
class MUOContainerAdmin(BaseAdmin):
    form = autocomplete_light.modelform_factory(CWE, fields="__all__")
    fields = ['name', 'cwes', 'misuse_case', 'new_misuse_case', 'status']
    list_display = ['name', 'status']
    readonly_fields = ['name', 'status']
    search_fields = ['name', 'status']
    date_hierarchy = 'created_at'
    inlines = [UseCaseAdminInLine]

    def get_queryset(self, request):
        """
            If user doesn't have access to view all MUO Containers (review), then limit to his own MUOs
            or to approved MUOs written by other contributors
        """
        qs = super(MUOContainerAdmin, self).get_queryset(request)
        if request.user.has_perm('muo.can_view_all'):
            return qs
        return qs.filter(Q(created_by=request.user) | Q(status='approved'))

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
                obj.action_approve(request.user)
                msg = "You have approved the submission"

            elif "_reject" in request.POST:
                reject_reason = request.POST.get('reject_reason_text', '')
                obj.action_reject(reject_reason, request.user)
                obj.save()
                msg = "The submission has been sent back to the author for review"

            elif "_submit_for_review" in request.POST:
                obj.action_submit()
                msg = "Your review request has been successfully submitted"

            elif "_edit" in request.POST:
                obj.action_save_in_draft()
                msg = "You can now edit the MUO"
                
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
        except ValidationError as e:
            # If incomplete MUO Container is attempted to be approved or submitted for review, a validation error will
            # be raised with an appropriate message
            msg = e.message
            self.message_user(request, msg, messages.ERROR)
            return HttpResponseRedirect(redirect_url)

        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)

