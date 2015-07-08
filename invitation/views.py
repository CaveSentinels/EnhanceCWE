from allauth.account import views


class MySignupView(views.SignupView):

    def get_form_class(self):
        """ Store the token and email in the session """
        if 'token' in self.request.GET and 'email' in self.request.GET:
            self.request.session['invite_email'] = self.request.GET['email']
            self.request.session['invite_token'] = self.request.GET['token']
        return super(MySignupView, self).get_form_class()


views.signup = MySignupView.as_view()
