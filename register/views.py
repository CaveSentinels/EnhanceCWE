from allauth.account import views
from allauth.account.views import SignupView
from allauth.utils import get_form_class
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account import app_settings

class CaptchaLoginView(views.LoginView):

    def get_form_kwargs(self):
        """ Pass the request object to the form to be able to access the session """
        kwargs = super(CaptchaLoginView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

# This will be the login view
login = CaptchaLoginView.as_view()

# Routing logout and password_change to allauth
logout = views.logout
password_change = views.password_change


class MySignupView(SignupView):

    def get_form_class(self):
        """ Store the token and email in the session """
        if 'token' in self.request.GET or 'email' in self.request.GET:
            self.request.session['invite_email'] = self.request.GET['email']
            self.request.session['invite_token'] = self.request.GET['token']
        return get_form_class(app_settings.FORMS, 'signup', self.form_class)


signup = MySignupView.as_view()