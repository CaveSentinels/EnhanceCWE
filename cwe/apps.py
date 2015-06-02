from django.apps import AppConfig

class CWEConfig(AppConfig):
    name = 'cwe'
    verbose_name = "CWE"

    def ready(self):
        # Importing autocomplete_registry only after models are ready and app is fully loaded
        import autocomplete_registry