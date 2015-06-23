# DJANGO IMPORTS
from django.conf import settings

# set the user as 'staff' automatically on registeration
SET_STAFF_ON_REGISTRATION = getattr(settings, "SET_STAFF_ON_REGISTRATION", True)
