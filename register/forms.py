from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from allauth.account.forms import SignupForm


class CustomSingupForm(SignupForm):
    """
    It is a Custom Registration Form class which overrides the default registration form class.
    Its purpose is to add two new fields to the registration form
    """

    first_name = forms.CharField(label=_('First name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30, required=True)
    recaptcha = ReCaptchaField(label="I'm a human")


    def __init__(self, *args, **kwargs):
        super(CustomSingupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                Field('username', placeholder=self.fields['username'].label, wrapper_class='col-sm-12'),
                css_class='col-sm-12',
            ),
            Div(
                Field('first_name', placeholder=self.fields['first_name'].label, wrapper_class="col-sm-6"),
                Field('last_name', placeholder=self.fields['last_name'].label, wrapper_class='col-sm-6'),
                css_class='col-sm-12',
            ),
            Div(
                Field('password1', placeholder=self.fields['password1'].label, wrapper_class="col-sm-6"),
                Field('password2', placeholder=self.fields['password2'].label, wrapper_class='col-sm-6'),
                css_class='col-sm-12',
            ),
            Div(
                Field('email', placeholder=self.fields['email'].label, wrapper_class='col-sm-12'),
                css_class='col-sm-12',
            ),
            Div(
                Field('recaptcha', placeholder=self.fields['recaptcha'].label, wrapper_class='col-sm-6'),
                css_class='col-sm-12',
            ),
        )
