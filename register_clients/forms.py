from register.forms import CustomSingupForm
from django import forms
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from allauth.account.forms import SignupForm, LoginForm
from allauth.account import app_settings
from allauth.account.forms import authenticate
from django.utils.translation import ugettext_lazy as _
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.account.models import EmailAddress


class CustomSignupFormClient(CustomSingupForm):
    """
    It is a Custom Registration Form class which overrides the default registration form class.
    Its purpose is to add two new fields to the registration form
    """

    role = forms.ChoiceField(label=_('Role'),
        choices = (
            ('Contributor', "Contributor"),
            ('Client', "Client")
        ),
        widget = forms.RadioSelect(),
        initial = 'Contributor',
    )

    def __init__(self, *args, **kwargs):
        super(CustomSignupFormClient, self).__init__(*args, **kwargs)
        layout_for_radio_button = Div(
                Field('role', placeholder=self.fields['role'].label, wrapper_class='col-sm-12'),
                css_class='col-sm-12',
            )

        original_helper = self.helper.layout
        original_helper.fields.append(layout_for_radio_button)

    def save(self, request):
        """
        We are overriding this method to save the extra information related to the user.
        In this case, this extra information is the role requested.
        """
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        self.setup_user_email(request, user, [])
        return user

    def setup_user_email(self, request, user, addresses):
        """
        This method actually performs the steps to create a email address object
        and save it in the database. The original implementation comes from
        allauth.account.utils
        """
        from allauth.account.models import EmailAddress
        from allauth.account.utils import user_email
        from allauth.account.utils import cleanup_email_addresses

        assert EmailAddress.objects.filter(user=user).count() == 0
        priority_addresses = []
        # Is there a stashed e-mail?
        adapter = get_adapter()
        stashed_email = adapter.unstash_verified_email(request)
        if stashed_email:
            priority_addresses.append(EmailAddress(user=user,
                                                   email=stashed_email,
                                                   primary=True,
                                                   verified=True))
        email = user_email(user)
        role = request.POST['role']

        # START: Add new field  requested_role here
        if email:
            priority_addresses.append(EmailAddress(user=user,
                                                   email=email,
                                                   primary=True,
                                                   verified=False,
                                                   requested_role = role
                                                   ))
        # END

        addresses, primary = cleanup_email_addresses(request,
                                                     priority_addresses
                                                     + addresses)
        for a in addresses:
            a.user = user
            a.save()
        EmailAddress.objects.fill_cache_for_user(user, addresses)
        if (primary
                and email
                and email.lower() != primary.email.lower()):
            user_email(user, primary.email)
            user.save()
        return primary