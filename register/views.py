from allauth.account import views


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
