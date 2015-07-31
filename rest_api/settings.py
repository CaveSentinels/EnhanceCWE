from django.conf import settings

# Specify how many CWEs are returned when suggesting CWEs according to given report content.
SUGGESTED_CWE_MAX_RETURN = getattr(settings, "SUGGESTED_CWE_MAX_RETURN", 10)
