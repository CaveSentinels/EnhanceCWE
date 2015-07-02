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
from django import forms
from django.forms.extras.widgets import *
from django.utils.safestring import mark_safe

from django.http import HttpResponseRedirect
from base.admin import BaseAdmin


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(UseCase)
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

    def has_delete_permission(self, request, obj=None):
        """
        Overriding the method such that the delete option on the UseCaseAdminInline form on change form
        is not available for the users except the original author. The delete option is only available
        to the original author if the related MUOContainer is in draft state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(UseCaseAdminInLine, self).has_delete_permission(request, obj=None)
        else:
            # This is change form. Only original author is allowed to delete the UseCase from the related
            # MUOContainer if it is in 'draft' state
            if request.user == obj.created_by and obj.status in ('draft', 'rejected'):
                return super(UseCaseAdminInLine, self).has_delete_permission(request, obj=None)
            else:
                # Set deletion permission to False
                return False


    def get_readonly_fields(self, request, obj=None):
        """
        Overriding the method such that all the fields on the UseCaseAdminInline form on change form
        are read-only for all the users except the original author. Only the original author can edit
        the fields that too when the related MUOContainer is in the 'draft' state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(UseCaseAdminInLine, self).get_readonly_fields(request, obj)
        else:
            # This is the change form. Only the original author is allowed to edit the UseCase if the
            # related MUOContainer is in the 'draft' state
            if request.user == obj.created_by and obj.status == 'draft':
                return super(UseCaseAdminInLine, self).get_readonly_fields(request, obj)
            else:
                # Set all the fields as read-only
                return list(set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))

    def get_max_num(self, request, obj=None, **kwargs):
        """
        Overriding the method such that the 'Add another Use Case' option on the UseCaseAdminInline form
        on change form is not available for the users except the original author. The 'Add another UseCase'
        option is only available to the original author if the related MUOContainer is in draft state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(UseCaseAdminInLine, self).get_max_num(request, obj=None, **kwargs)
        else:
            # This is change form. Only original author is allowed to add another Use Case in the
            # MUOContainer if it is in 'draft' state
            if request.user == obj.created_by and obj.status == 'draft':
                return super(UseCaseAdminInLine, self).get_max_num(request, obj=None, **kwargs)
            else:
                # No 'Add another Use Case' button
                return 0


@admin.register(MisuseCase)
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
            misuse_cases = MisuseCase.objects.approved()
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


    def changelist_view(self, request, extra_context=None):
        if request.GET.get('_popup', False):
            #  If its a popup request let super handle it
            return super(MisuseCaseAdmin, self).changelist_view(request, extra_context)

        urls = super(MisuseCaseAdmin, self).get_urls()

        # Render the custom template for the changelist_view
        context = {}

        return render(request, 'admin/muo/misusecase/misusecase_search.html', context)


class MUOContainerAdminForm(autocomplete_light.ModelForm):
    # Create a radio button type choice field for selecting the existing/new misuse case
    choice = forms.TypedChoiceField(required=False, choices=(('existing', 'Existing Misuse Case'), ('new', 'New Misuse Case')),
                                    widget=forms.RadioSelect, initial='existing',
                                    label='Select from the options below')

    def __init__(self, *args, **kwargs):
        # Overriding the init method so that the initial value for the 'choice' can be set. Also
        # the required/optional fields are set here

        super(MUOContainerAdminForm, self).__init__(*args, **kwargs)

        if self.instance.pk is None:
            # This is an 'add' form because no MUOContainer database object exists.
            # Make both the fields (misuse case and new misuse case) required, so that
            # they show up as required on the form.
            # 'choice' is also True because we want validator for choice field to be enabled
            self.fields['choice'].required = True
            self.fields['misuse_case'].required = True
            self.fields['new_misuse_case'].required = True
        else:
            # This is the 'change' form
            if self.instance.status == 'draft':
                # Both the fields should be required because the user can change the selection
                # 'choice' is also True because we want validator for choice field to be enabled
                self.fields['choice'].required = True
                self.fields['misuse_case'].required = True
                self.fields['new_misuse_case'].required = True

                # If no misuse case is related, this means the user originally selected the
                # New Misuse Case option, so default selection should be new misuse case
                # otherwise the default selection should be the Existing Misuse Case
                if self.instance.misuse_case is None:
                    # Custom misuse case was created, default selection should be new misuse case
                    self.fields['choice'].initial = 'new'
                else:
                    # An existing misuse case was selected, default selection should be existing misuse case
                    self.fields['choice'].initial = 'existing'
            else:
                # If the status is not 'draft', the choice field won't be shown on the form
                # and the validator should also be turned off for it.
                self.fields['choice'].required = False


    def clean(self):
        cleaned_data = self.cleaned_data

        if cleaned_data['choice'] == 'existing':
            # If the selection for the choice field is existing misuse case, new_misuse_case
            # needs to be removed from the _errors because we have set it as a required field
            # in __init__ but since no value is entered for it, the validation would fail
            # and it would be present in the _errors. We need to remove it otherwise form
            # will keep complaining about it.
            if 'new_misuse_case' in self._errors:
                del self._errors['new_misuse_case']
                self.cleaned_data['new_misuse_case'] = None
        elif cleaned_data['choice'] == 'new':
            # If the selection for the choice field is new misuse case, misuse_case
            # needs to be removed from the _errors because we have set it as a required field
            # in __init__ but since no value is entered for it, the validation would fail
            # and it would be present in the _errors. We need to remove it otherwise form
            # will keep complaining about it.
            if 'misuse_case' in self._errors:
                del self._errors['misuse_case']
                self.cleaned_data['misuse_case'] = None

        return cleaned_data


    def save(self, commit=True):
        # Overriding the save method because we want to capture either value of misuse_case
        # field or the new_misuse_case field but not both. So, based on the choice field selection
        # by the user, we would either capture value of misuse_case or new_misuse_case and set
        # the other one to None
        model = super(MUOContainerAdminForm, self).save(commit=False)

        if model.status == 'draft':
            # If the status of the MUOContainer object is 'draft', check the user selection
            # for 'choice' option and accordingly set either misuse_case or the new_use_case to None
            if 'choice' in self.fields:
                if self.cleaned_data['choice'] == 'existing':
                    model.new_misuse_case = None
                else:
                    model.misuse_case = None
            model.save()
        return model


@admin.register(MUOContainer)
class MUOContainerAdmin(BaseAdmin):
    form = MUOContainerAdminForm
    fields = ['name', 'cwes', 'choice', 'misuse_case', 'new_misuse_case', 'status']
    list_display = ['name', 'status']
    readonly_fields = ['name', 'status']
    search_fields = ['name', 'status']
    date_hierarchy = 'created_at'
    inlines = [UseCaseAdminInLine]

    def get_form(self, request, obj=None, **kwargs):
        # Overriding this method so that the 'choice' field can be added or removed
        # from the form based on the type i.e. add or change. Also, if it is change
        # form, 'choice' field can be added/removed based on the status of the MUOContainer

        # get base form object
        form = super(MUOContainerAdmin,self).get_form(request, obj, **kwargs)
        if obj is not None:
            # It's a change form. Only show choice field if the status is draft.
            if obj.status == 'draft':
                # show choice field at 2nd position
                if 'choice' not in self.fields:
                    self.fields.insert(2, 'choice')
            else:
                # If status is not draft, do not show the choice field on the form
                if 'choice' in self.fields:
                    self.fields.remove('choice')
        else:
            # If add form, show choice field at 2nd position
            if 'choice' not in self.fields:
                self.fields.insert(2, 'choice')
        return form


    def get_actions(self, request):
        """
        Overriding the method in order to disable the delete selected (and bulk delete) option the
        changelist form
        """
        actions = super(MUOContainerAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


    def get_queryset(self, request):
        """
            If user doesn't have access to view all MUO Containers (review), then limit to his own MUOs
            or to approved MUOs written by other contributors
        """
        qs = super(MUOContainerAdmin, self).get_queryset(request)
        if request.user.has_perm('muo.can_view_all'):
            return qs
        return qs.filter(Q(created_by=request.user) | Q(status='approved'))


    def get_readonly_fields(self, request, obj=None):
        """
        Overriding the method such that the change form is read-only for all the user. Only the original
        author of the MUOContainer can edit it that too only when MUOContainer is in 'draft' state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(MUOContainerAdmin, self).get_readonly_fields(request, obj)
        else:
            # This is change form. Only original author is allowed to edit the MUOContainer in draft state
            if request.user == obj.created_by and obj.status == 'draft':
                return super(MUOContainerAdmin, self).get_readonly_fields(request, obj)
            else:
                # Set all the fields as read-only
                return list(set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))


    def has_delete_permission(self, request, obj=None):
        """
        Overriding the method such that the delete option on the change form is not available
        for the users except the original author. The delete option is only available to the
        original author if the related MUOContainer is in draft state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(MUOContainerAdmin, self).has_delete_permission(request, obj=None)
        else:
            # This is change form. Only original author is allowed to delete the MUOContainer
            # and that too if it is in 'draft' state
            if request.user == obj.created_by and obj.status in ('draft', 'rejected'):
                return super(MUOContainerAdmin, self).has_delete_permission(request, obj=None)
            else:
                # Set deletion permission to False
                return False



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
                msg = "The submission has been sent back to the author for review"

            elif "_submit_for_review" in request.POST:
                obj.action_submit()
                msg = "Your review request has been successfully submitted"

            elif "_edit" in request.POST:
                obj.action_save_in_draft()
                msg = "You can now edit the MUO"

            elif "_promote" in request.POST:
                obj.action_promote(request.user)
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



@admin.register(IssueReport)
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
        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            # url will be /admin/muo/issuereport/new_report
            url(r'new_report/$', self.admin_site.admin_view(self.new_report_view), name='%s_%s_new_report' % info),
            url(r'add_report/$', self.admin_site.admin_view(self.render_add_report), name='%s_%s_add_report' % info),
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
            return TemplateResponse(request, "admin/muo/issuereport/new_report.html", context)
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
                new_object = form.save()
                self.message_user(request, "Report %s has been created will be reviewed by our reviewers" % new_object.name , messages.SUCCESS)
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