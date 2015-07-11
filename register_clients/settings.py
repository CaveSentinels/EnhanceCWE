from django.conf import settings

# set the user as 'staff' automatically on registeration
SET_STAFF_ON_REGISTRATION = getattr(settings, "SET_STAFF_ON_REGISTRATION", True)

NUMBER_OF_FAILED_LOGINS_BEFORE_CAPTCHA = getattr(settings, "NUMBER_OF_FAILED_LOGINS_BEFORE_CAPTCHA", 3)
