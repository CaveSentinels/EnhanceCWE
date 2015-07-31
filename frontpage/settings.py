from django.conf import settings

# set the number of CWEs displayed in the dropdown select
SELECT_CWE_PAGE_LIMIT = getattr(settings, "SELECT_CWE_PAGE_LIMIT", 10)
