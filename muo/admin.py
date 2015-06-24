from django.db.models import Q
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.template.response import TemplateResponse
from django.conf.urls import url
import autocomplete_light
from models import *
from django.utils.safestring import mark_safe

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
            url(r'^misusecases/$', self.admin_site.admin_view(self.misusecases_view)),
            url(r'^usecases/$', self.admin_site.admin_view(self.usecases_view)),
        ]

        return additional_urls + urls


    def misusecases_view(self, request):
        if request.method != 'POST':
            raise Http404("Invalid access using GET request!")

        #  Get the selected CWE ids from the request
        selected_cwe_ids = request.POST.getlist('cwe_ids', None)

        if len(selected_cwe_ids) == 0:
            # If list of CWE ids is empty return all the misuse cases
            misuse_cases = MisuseCase.objects.all()
        else:
            #  Get the use cases for the selected CWE ids
            misuse_cases = MisuseCase.objects.filter(cwes__in=selected_cwe_ids)

        #  Create a context with all the corresponding misuse cases
        context = {'misuse_cases': misuse_cases}

        return TemplateResponse(request, "admin/muo/misusecase/misusecase.html", context)


    def usecases_view(self, request):
        if request.method != 'POST':
            raise Http404("Invalid access using GET request!")

        misuse_case_id = request.POST['misuse_case_id']

        try:
            # Fetch the misuse case object for the misuse_case_id
            misuse_case = MisuseCase.objects.get(pk=misuse_case_id)
        except ObjectDoesNotExist as e:
            raise Http404("Misuse case with id %d doesn't exist", misuse_case_id)

        #  Create a context with all the corresponding use cases
        context = {'use_cases': misuse_case.usecase_set.all()}

        return TemplateResponse(request, "admin/muo/misusecase/usecase.html", context)


    # def changelist_view(self, request, extra_context=None):
    #     if request.GET.get('_popup', False):
    #         #  If its a popup request let super handle it
    #         return super(MisuseCaseAdmin, self).changelist_view(request, extra_context)
    #
    #     urls = super(MisuseCaseAdmin, self).get_urls()
    #
    #     # Render the custom template for the changelist_view
    #     context = {}
    #
    #     return render(request, 'admin/muo/misusecase/misusecase_search.html', context)


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

            elif "_promote" in request.POST:
                obj.action_promote()
                msg = "This MUO has been promoted and now everyone will have access to it."
                
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


@admin.register(IssueReport, site=admin_site)
class IssueReportAdmin(BaseAdmin):
    form = autocomplete_light.modelform_factory(IssueReport, fields="__all__")
    fields = [('name', 'status'), 'type', 'usecase', 'usecase_duplicate', 'description', ('created_by', 'created_at')]
    list_display = ['name', 'type', 'created_by', 'created_at', 'status',]
    readonly_fields = ['name', 'status', 'created_by', 'created_at']
    search_fields = ['name', 'usecase__id', 'usecase__name', 'created_by__name']
    list_filter = ['type', 'status']
    date_hierarchy = 'created_at'


    def get_urls(self):
        urls = super(IssueReportAdmin, self).get_urls()
        my_urls = [
            # url will be /admin/muo/issuereport/new_report
            url(r'new_report/$', self.admin_site.admin_view(self.new_report_view)),
            url(r'add_report/$', self.admin_site.admin_view(self.render_add_report)),
        ]
        return my_urls + urls


    def new_report_view(self, request):
        """
        This view is called by muo search using ajax to display the report issue popup
        """
        if request.method == "POST":
            # read the usecase_id that triggered this action
            usecase_id = request.POST.get('usecase_id')
            usecase = get_object_or_404(UseCase, pk=usecase_id)

            # Render issue report form and default initial values, if any
            ModelForm = self.get_form(request)
            initial = self.get_changeform_initial_data(request)
            initial['usecase'] = usecase
            form = ModelForm(initial=initial)

            context = dict(
                # Include common variables for rendering the admin template.
                self.admin_site.each_context(request),
                form=form,
                usecase=usecase,
            )
            return TemplateResponse(request, "admin/muo/reportissue/new_report.html", context)
        else:
            raise Http404("Invalid access using GET request!")


    def render_add_report(self, request):
        """
        Handle adding new report created using muo search popup
        """

        if request.method == 'POST':

            ModelForm = self.get_form(request)
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():

                # Check if this user already created a report for this usecase
                usecase_id = request.POST.get('usecase')
                previous_report = IssueReport.objects.filter(created_by=request.user, usecase=usecase_id)

                if previous_report:
                    self.message_user(request, "You have already created an issue report for this use case (%s)!" % previous_report[0].name, messages.ERROR)

                else:
                    new_object = form.save()
                    self.message_user(request, "Report %s has been created will be reviewed by our admins" % new_object.name , messages.SUCCESS)
            else:
                # submitted form is invalid
                errors = ["%s: %s" % (form.fields[field].label, error[0]) for field, error in form.errors.iteritems()]
                errors = '<br/>'.join(errors)
                self.message_user(request, mark_safe("Invalid report content!<br/>%s" % errors) , messages.ERROR)

            # Go back to misuse case view
            opts = self.model._meta
            post_url = reverse('admin:%s_%s_changelist' %
                               (opts.app_label, 'misusecase'),
                               current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)

            return HttpResponseRedirect(post_url)

        else:
            raise Http404("Invalid access using GET request!")