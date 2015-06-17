from django.apps import AppConfig

class MUOConfig(AppConfig):
    name = 'muo'
    verbose_name = "MUO"

    def ready(self):
        # Importing autocomplete_registry only after models are ready and app is fully loaded
        import autocomplete_registry