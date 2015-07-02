from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.core.urlresolvers import reverse
from allauth.utils import build_absolute_uri
from django.core.mail import send_mail
from allauth.account import app_settings
from django.template.loader import get_template
from django.template import Context



class EmailInvitation(models.Model):
    email_address = models.CharField(max_length=100)

    def send_invitation(self,request):
        key = get_random_string(64).lower()
        activate_url = '/accounts/signup/'+key
        activate_url = build_absolute_uri(request,
                                          activate_url,
                                          protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
        send_mail("Join",get_template('admin/invitation/emailinvitation/invitation.html').render(
                    Context({
                        'activate_url':activate_url,
                        })
                    ), "enhancedcwe@gmail.com",self.email_address,fail_silently=True)



