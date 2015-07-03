from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from allauth.exceptions import ImmediateHttpResponse
from allauth.account import signals
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation, get_login_redirect_url
from allauth.account.models import EmailAddress
from invitation.models import EmailInvitation
from urlparse import urlparse, parse_qs


def perform_login(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False):
    """
    Keyword arguments:

    signup -- Indicates whether or not sending the
    email is essential (during signup), or if it can be skipped (e.g. in
    case email verification is optional and we are only logging in).
    """

    check_if_invited(request, user)

    # Local users are stopped due to form validation checking
    # is_active, yet, adapter methods could toy with is_active in a
    # `user_signed_up` signal. Furthermore, social users should be
    # stopped anyway.
    if not user.is_active:
        return HttpResponseRedirect(reverse('account_inactive'))

    from allauth.account.models import EmailAddress
    has_verified_email = EmailAddress.objects.filter(user=user,
                                                     verified=True).exists()
    if email_verification == EmailVerificationMethod.NONE:
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


def check_if_invited(request, user):
    url = urlparse(str(request.META['HTTP_REFERER']))

    # check if coming from registration page
    if url.path == reverse('account_signup'):
        # Here I am checking if there is some token in the query string or not.
        # If there is a token then verify it and set the EmailVerificationMethod = NONE
        params = parse_qs(url.query)

        if 'token' in params and 'email' in params:
            email_local = params['email'][0]
            token_local = params['token'][0]
        elif 'invite_email' in request.session and 'invite_token' in request.session:
            email_local = request.session['invite_email']
            token_local = request.session['invite_token']

        if EmailInvitation.objects.filter(email=email_local, key=token_local).exists():
            email_obj = EmailAddress.objects.get(user=user, email=email_local)
            email_obj.verified = True
            email_obj.save()

            if 'invite_email' in request.session and 'invite_token' in request.session:
                del request.session['invite_email']
                del request.session['invite_token']


from allauth.account import utils
utils.perform_login = perform_login