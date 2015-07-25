from django.apps import AppConfig

class InvitationConfig(AppConfig):
    """
    Creating an AppConfig to load the views when the application is ready.
    The reason we are explicitly loading the views is because we are doing monkey patching in views.py
    """
    name = 'invitation'
    verbose_name = "User Invitation"

    def ready(self):
        from .views import *