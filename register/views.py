from allauth.account.views import SignupView
from allauth.account.utils import complete_signup
from django.contrib.auth.models import Group, User
from allauth.utils import build_absolute_uri



# from django.views.decorators.csrf import csrf_protect

class MySignupView(SignupView):

    # success_url = '/app/login/'


    # from django.utils.decorators import method_decorator
    # @method_decorator(csrf_protect)
    def form_valid(self, form):
        user = form.save(self.request)
        user_in_db = User.objects.filter(username=user.username)
        user_id = user_in_db[0].id
        email = EmailAddress.objects.get(id=user_id)
        email.verified = True
        email.save()

        return complete_signup(self.request, user, 'none', self.get_success_url())

    # def form_valid(self, form):
    #     user = form.save(self.request)
    #     return complete_signup(self.request, user,
    #                            app_settings.EMAIL_VERIFICATION,
    #                            self.get_success_url())


signup = MySignupView.as_view()
