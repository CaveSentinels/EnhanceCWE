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

    if not user.is_active:
        return HttpResponseRedirect(reverse('account_inactive'))


    from urlparse import urlparse
    url = urlparse(str(request.META['HTTP_REFERER']))


    # Here I am checking if there is some token in the query string or not.
    # If there is a token then verify it and set the EmailVerificationMethod = NONE
    if not url.query is None:
        token_from_url = url.query.split('&')[0].split('=')[1]
        email_from_url = url.query.split('&')[1].split('=')[1]
        from invitation.models import EmailInvitation
        if EmailInvitation.objects.filter(email_address=email_from_url, key=token_from_url).exists():
            email_verification = EmailVerificationMethod.NONE





    from allauth.account.models import EmailAddress
    has_verified_email = EmailAddress.objects.filter(user=user, verified=True).exists()


    if email_verification == EmailVerificationMethod.NONE:
        activate_user(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False)

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
    user_id_in_db = user_in_db[0].id
    email = EmailAddress.objects.get(user_id=user_id_in_db)
    email.verified = True
    email.save()


from allauth.account import utils
utils.perform_login = perform_login