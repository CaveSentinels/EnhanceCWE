from urlparse import urlparse, parse_qs

from django.core.urlresolvers import reverse
from allauth.account.models import EmailAddress

from invitation.models import EmailInvitation


def check_if_invited(request, user, *args, **kwargs):
    """ This method should be registered in ACCOUNT_EXTRA_PRE_LOGIN_STEPS to check if user came from invitation link """
    url = urlparse(str(request.META['HTTP_REFERER']))

    # check if coming from registration page
    if url.path == reverse('account_signup'):
        # Here I am checking if there is some token in the query string or not.
        # If there is a token then verify it and set the EmailVerificationMethod = NONE
        params = parse_qs(url.query)
        email_local = None
        token_local = None

        if 'token' in params and 'email' in params:
            email_local = params['email'][0]
            token_local = params['token'][0]
        elif 'invite_email' in request.session and 'invite_token' in request.session:
            email_local = request.session['invite_email']
            token_local = request.session['invite_token']

        if email_local and token_local:
            if EmailInvitation.objects.filter(email=email_local, key=token_local).exists():
                email_obj = EmailAddress.objects.get(user=user, email=email_local)
                email_obj.verified = True
                email_obj.save()

            if 'invite_email' in request.session:
                del request.session['invite_email']

            if 'invite_token' in request.session:
                del request.session['invite_token']