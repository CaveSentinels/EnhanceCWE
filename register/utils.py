try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


from django.contrib import messages
from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from allauth.exceptions import ImmediateHttpResponse


from allauth.account import signals
from allauth.account.app_settings import EmailVerificationMethod

from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation, get_login_redirect_url
from django.contrib.auth.models import Group, User
from allauth.account.models import EmailAddress

def perform_login(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False):
    """
    Keyword arguments:

    signup -- Indicates whether or not sending the
    email is essential (during signup), or if it can be skipped (e.g. in
    case email verification is optional and we are only logging in).
    """
    # Local users are stopped due to form validation checking
    # is_active, yet, adapter methods could toy with is_active in a
    # `user_signed_up` signal. Furthermore, social users should be
    # stopped anyway.
    if not user.is_active:
        return HttpResponseRedirect(reverse('account_inactive'))

    # request.REQUEST.dicts[0]['invite'] = 'yes'
    # if request.REQUEST.dicts[0]['invite'] == 'yes':
    #     email_verification = EmailVerificationMethod.NONE


    from allauth.account.models import EmailAddress
    has_verified_email = EmailAddress.objects.filter(user=user, verified=True).exists()

    if email_verification == EmailVerificationMethod.NONE:
        activate_user(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False)
        pass

    elif email_verification == EmailVerificationMethod.OPTIONAL:
        # In case of OPTIONAL verification: send on signup.
        if not has_verified_email and signup:
            send_email_confirmation(request, user, signup=signup)
    elif email_verification == EmailVerificationMethod.MANDATORY:
        if not has_verified_email:
            send_email_confirmation(request, user, signup=signup)
            return HttpResponseRedirect(
                reverse('account_email_verification_sent'))
    try:
        get_adapter().login(request, user)
        response = HttpResponseRedirect(
            get_login_redirect_url(request, redirect_url))

        if signal_kwargs is None:
            signal_kwargs = {}
        signals.user_logged_in.send(sender=user.__class__,
                                    request=request,
                                    response=response,
                                    user=user,
                                    **signal_kwargs)
        get_adapter().add_message(request,
                                  messages.SUCCESS,
                                  'account/messages/logged_in.txt',
                                  {'user': user})
    except ImmediateHttpResponse as e:
        response = e.response
    return response

def activate_user(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False):
    user_in_db = User.objects.filter(username=user.username)
    user_id = user_in_db[0].id
    email = EmailAddress.objects.get(id=user_id)
    email.verified = True
    email.save()


from allauth.account import utils
utils.perform_login = perform_login