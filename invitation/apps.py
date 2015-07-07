from django.apps import AppConfig

class InvitationConfig(AppConfig):
    name = 'invitation'
    verbose_name = "User Invitation"

    def ready(self):
        from .views import *