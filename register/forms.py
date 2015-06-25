from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, MultiField, Div
from crispy_forms.bootstrap import AppendedText, InlineField


class CustomRegistrationForm(RegistrationFormUniqueEmail):
    """
    It is a Custom Registration Form class which overrides the default registration form class.
    Its purpose is to add two new fields to the registration form
    """
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(),
                                label=_("Username"),
                                error_messages={
                                    'invalid': _("This value must contain "
                                                 "only letters, numbers and "
                                                 "underscores.")
                                })
    first_name = forms.CharField(label=_('First name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30, required=True)

    email1 = forms.EmailField(widget=forms.TextInput(), required=True, max_length=80, label=_("E-mail"))
    email2 = forms.EmailField(widget=forms.TextInput(), required=True, max_length=80, label=_("E-mail (again)"))
    recaptcha = ReCaptchaField(label="I'm a human")


    def __init__(self, *args, **kwargs):
        super(CustomRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-2'
        # self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Field('username', placeholder=self.fields['username'].label, wrapper_class='col-sm-12'),
            Field('first_name', placeholder=self.fields['first_name'].label, wrapper_class="col-sm-6"),
            Field('last_name', placeholder=self.fields['last_name'].label, wrapper_class='col-sm-6'),

            # Field('first_name', placeholder=self.fields['first_name'].label, css_class='col-xs-5'),
            # Field('last_name', placeholder=self.fields['last_name'].label, css_class='col-xs-5'),
            Field('email1', placeholder=self.fields['email1'].label, wrapper_class='col-sm-6'),
            Field('email2', placeholder=self.fields['email2'].label, wrapper_class='col-sm-6'),
            Field('recaptcha', placeholder=self.fields['recaptcha'].label, wrapper_class='col-sm-6'),



        )
