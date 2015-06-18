from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm


class CustomRegistrationForm(RegistrationForm):
    """
    It is a Custom Registration Form class which overrides the default registration form class.
    Its purpose is to add two new fields to the registration form
    """
    first_name = forms.CharField(label=_('First name'),max_length=30,required=True)
    last_name = forms.CharField(label=_('Last name'),max_length=30,required=True)

