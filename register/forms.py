from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm
from captcha.fields import ReCaptchaField
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import admin



class CustomRegistrationForm(RegistrationForm):
    """
    It is a Custom Registration Form class which overrides the default registration form class.
    Its purpose is to add two new fields to the registration form
    """
    first_name = forms.CharField(label=_('First name'),max_length=30,required=True)
    last_name = forms.CharField(label=_('Last name'),max_length=30,required=True)

    recaptcha = ReCaptchaField(label="I'm a human")



class MyAuthenticationForm(AuthenticationForm):
    recaptcha = ReCaptchaField(label="I'm a human")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        from django.contrib.auth import authenticate
        if username and password:
            self.user_cache = authenticate(username=username, password=password)


            if self.user_cache is None:

                # START: Required change for captcha integration
                # Here we are storing the invalid login attempts in the session
                if 'invalid_login' not in self.request.session:
                    self.request.session["invalid_login"] = 1
                else:
                    self.request.session["invalid_login"] = self.request.session["invalid_login"] + 1

                # END

                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.request.session["invalid_login"] = 0
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


admin.autodiscover()
admin.site.login_form = MyAuthenticationForm