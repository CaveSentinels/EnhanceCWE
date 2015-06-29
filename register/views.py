from django.contrib import admin
from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login,
)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters


@never_cache
def login(self, request, extra_context=None):
    """
    Displays the login form for the given HttpRequest.
    """
    if request.method == 'GET' and self.has_permission(request):
        # Already logged-in, redirect to admin index
        index_path = reverse('admin:index', current_app=self.name)
        return HttpResponseRedirect(index_path)

    from django.contrib.admin.forms import AdminAuthenticationForm
    context = dict(self.each_context(request), title=_('Log in'), app_path=request.get_full_path(),)



    if (REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST):
        context[REDIRECT_FIELD_NAME] = request.get_full_path()

    context.update(extra_context or {})

    # START: Required change for captcha integration
    if 'invalid_login' in request.session:
        if request.session["invalid_login"] >= 2:
            context['display_capcha'] = True
        else:
            context['display_capcha'] = False

    else:
        context['display_capcha'] = False
    # END


    defaults = {
            'extra_context': context,
            'current_app': self.name,
            'authentication_form': self.login_form or AdminAuthenticationForm,
            'template_name': self.login_template or 'admin/login.html',
    }

    return login_auth(request, **defaults)


# monkey patch index()
admin.AdminSite.login = login

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login_auth(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)

        # START: Required change for captcha integration
        # Here we suppress the Captcha validation error when it is not supposed to be shown on the UI
        if extra_context['display_capcha'] == False and 'recaptcha' in form.errors:
            del form.errors['recaptcha']
        # END


        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)