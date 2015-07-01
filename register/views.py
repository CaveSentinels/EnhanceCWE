from allauth.account.views import SignupView
from allauth.account.utils import complete_signup
from django.contrib.auth.models import Group, User
from allauth.account.models import EmailAddress

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

        return complete_signup(self.request, user, None, self.get_success_url())


signup = MySignupView.as_view()