"""
Django settings for EnhancedCWE project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-wt!%_nsos-5nf5$$ojt=88vv&odc@etnuvtg%oa8!m)8veth5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Application definition

SITE_TITLE = 'SERF'
SENDER_EMAIL = 'SERF'

INSTALLED_APPS = (
    'base',
    'invitation',
    'muo',
    'admin_lte',
    'django_admin_bootstrapped',
    'autocomplete_light',
    'captcha',
    'frontpage',
    'crispy_forms',
    'comments',
    'fluent_comments',
    'django_comments',
    'django.contrib.sites',
    'register',
    'allauth',
    'allauth.account',
    'register_approval',
    'register_clients',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_api',
    'cwe',
    'user_profile',
    'muo_mailer',
    'widget_tweaks',
    'mailer',
)

# Email settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'serf.noreply'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = 'serf_masre'


# START: allauth settings
LOGIN_REDIRECT_URL = '/app/'
ACCOUNT_FORMS = {'signup': 'register_clients.forms.CustomSignupFormClient',
                 'login': 'register.forms.CaptchaLoginForm',
                 }
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
# END

# START: register settings
ACCOUNT_EXTRA_PRE_LOGIN_STEPS = ['invitation.utils.verify_email_if_invited',
                                 'register_approval.utils.check_admin_approval']
# END

# START: Capcha settings
RECAPTCHA_PUBLIC_KEY = '6LcDAg4TAAAAAAyKuVzKReWYligCYbtgkSaMy-jC'
RECAPTCHA_PRIVATE_KEY = '6LcDAg4TAAAAAOPMjRxH6nv3WcXPk00CEx3JU8Ks'
NOCAPTCHA=False
RECAPTCHA_USE_SSL = True
# END


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'EnhancedCWE.middleware.WhodidMiddleware',
)

ROOT_URLCONF = 'EnhancedCWE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'allauth.account.context_processors.account',
            ],
        },
    },
]

from django.contrib import messages
MESSAGE_TAGS = {
            messages.SUCCESS: 'alert-success success',
            messages.WARNING: 'alert-warning warning',
            messages.ERROR: 'alert-danger error',
            messages.INFO: 'alert-success success',
}

WSGI_APPLICATION = 'EnhancedCWE.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(),
}
# Enable Connection Pooling
DATABASES['default']['ENGINE'] = 'django_postgrespool'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


# Settings for the REST framework
REST_FRAMEWORK = {
    # Use token to authenticate users.
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    # Only authenticated users can view or change information.
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
COMMENTS_APP = 'fluent_comments'
FLUENT_COMMENTS_EXCLUDE_FIELDS = ('name', 'email', 'url')
FLUENT_COMMENTS_USE_EMAIL_NOTIFICATION = False
FLUENT_COMMENTS_REPLACE_ADMIN = False