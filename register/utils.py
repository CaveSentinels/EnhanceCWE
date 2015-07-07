from django.conf import settings
from django.utils import importlib
import six
import allauth

# Keep reference of original perform login before it gets monkey patched
original_perform_login = allauth.account.utils.perform_login

def perform_login(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False):
    """
    This method adds hooks for other applications to add behaviors to the original perform_login found in allauth
    """

    extra_pre_login_steps = getattr(settings, 'ACCOUNT_EXTRA_PRE_LOGIN_STEPS', [])
    for step in extra_pre_login_steps:
        method = import_attribute(step)
        method(**locals())

    # Original Result
    res = original_perform_login(request, user, email_verification, redirect_url=redirect_url, signal_kwargs=signal_kwargs, signup=signup)

    extra_post_login_steps = getattr(settings, 'ACCOUNT_EXTRA_POST_LOGIN_STEPS', [])
    for step in extra_post_login_steps:
        method = import_attribute(step)
        method(**locals())

    return res


def import_attribute(path):
    """ Proper import of methods passed as string of full qualified name """
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


# Monkey patch perform login
from allauth.account import utils
utils.perform_login = perform_login
