from crispy_forms.bootstrap import InlineRadios
from django import forms
from crispy_forms.layout import Div
from django.utils.translation import ugettext_lazy as _
from allauth.account.models import EmailAddress

from register.forms import CustomSignupForm


class CustomSignupFormClient(CustomSignupForm):
    """
    It is a Custom Registration Form class which adds extra fields to the default registration form.
    Here we are adding 'role' as an extra field.
    """

    role = forms.ChoiceField(label=_('Role'), choices=(('contributor', "Contributor"), ('client', "Client")),
                             widget=forms.RadioSelect(), initial='contributor')

    def __init__(self, *args, **kwargs):
        super(CustomSignupFormClient, self).__init__(*args, **kwargs)
        layout_for_radio_button = Div(
            InlineRadios('role', wrapper_class='col-sm-12'),
            css_class='col-sm-12'
        )
        self.helper.layout.insert(4, layout_for_radio_button)


    def save(self, request):
        """
        We are overriding this method to save the extra information related to the user.
        In this case, this extra information is the role requested.
        """
        user = super(CustomSignupFormClient, self).save(request)
        email = EmailAddress.objects.filter(user=user)[0]
        role = request.POST.get('role')
        if role:
            email.requested_role = role
            email.save()
        return user
