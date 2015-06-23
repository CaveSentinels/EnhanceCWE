from registration.backends.default import DefaultRegistrationBackend
from register.forms import CustomRegistrationForm
from registration.conf import settings
from registration.models import RegistrationProfile
from registration import signals


class CustomRegistrationBackend(DefaultRegistrationBackend):
    """
    It is a registration backend class which overrides the default registration backend class.
    Its purpose are two fold -
    1. To return the Custom Registration Form which we have created in register/forms.py
    instead of the default form.
    2. To add first_name and last_name fields to the created user account
    """

    def get_registration_form_class(self):
        """
        It overrides the get_registration_form_class to return the custom registration form instead of the defalt one
        :param: None
        :return: CustomRegistrationForm
        """
        return CustomRegistrationForm

    def register(self, username, email, request, supplement=None, send_email=None):
        """
        It overrides the register method to add first_name and last_name fields to the created user account.
        :param: None
        :return: CustomRegistrationForm
        """

        if send_email is None:
            send_email = settings.REGISTRATION_REGISTRATION_EMAIL

        new_user = RegistrationProfile.objects.register(
            username, email, self.get_site(request),
            send_email=send_email,
        )

        # START: Add new fields here
        # Extract the first_name and last_name from the POST request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Save these to the user object
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        # END

        profile = new_user.registration_profile

        if supplement:
            supplement.registration_profile = profile
            supplement.save()

        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            profile=new_user.registration_profile,
            request=request,
        )

        return new_user