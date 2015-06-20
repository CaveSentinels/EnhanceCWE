from django.dispatch import receiver
from muo.signals import *
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from user_profile.models import *
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
import constants


"""
All of these methods are the handlers for the signals defined in signals.py in the
MUO Application.
They create the email body by fetching the parameters and send the email
"""

# This method will send an email when an MUO gets accepted
@receiver(muo_accepted)
def on_muo_accepted(sender, instance, **kwargs):
    if instance.created_by.profile.notify_muo_accepted:
        subject = constants.MUO_ACCEPTED_SUBJECT
        action = constants.ACCEPTED
        generate_email(instance, subject, action)

# This method will send an email when an MUO gets rejected
@receiver(muo_rejected)
def on_muo_rejected(sender, instance, **kwargs):
    if instance.created_by.profile.notify_muo_rejected:
        subject = constants.MUO_REJECTED_SUBJECT
        action = constants.REJECTED
        generate_email(instance, subject, action)

# This method will send an email when the MUO is voted up by any user
@receiver(muo_voted_up)
def on_muo_voted_up(sender, instance, **kwargs):
    if instance.created_by.profile.notify_muo_voted_up:
        subject = constants.MUO_VOTED_UP_SUBJECT
        action = constants.VOTEDUP
        generate_email(instance, subject, action)

# This method will send an email when the MUO is voted down by any user
@receiver(muo_voted_down)
def on_muo_voted_down(sender, instance, **kwargs):
    if instance.created_by.profile.notify_muo_voted_down:
        subject = constants.MUO_VOTED_DOWN_SUBJECT
        action = constants.VOTEDDOWN
        generate_email(instance, subject, action)

# This method will send an email when the MUO is commented upon
@receiver(muo_commented)
def on_muo_commented(sender, instance,**kwargs):
    if instance.created_by.profile.notify_muo_commented:
        subject = constants.MUO_COMMENTED_SUBJECT
        action = constants.COMMENTED
        generate_email(instance, subject, action)

# TODO: All other reviewers should be notified - need to handle that
@receiver(muo_duplicate)
def on_muo_duplicate(sender,instance, **kwargs):
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # TODO: We still have not finalized the permissions required for users when the muo is marked as duplicate
    # TODO: Once finalized, just replace it in codename__in field below
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(profile__notify_muo_duplicate=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm))
    emails = [user.email for user in users]
    subject = constants.MUO_DUPLICATE_SUBJECT
    action = constants.DUPLICATE
    generate_bulk_email(instance, subject, action, emails)


# TODO: All other reviewers should be notified  - need to handle that
@receiver(muo_inappropriate)
def on_muo_inappropriate(sender,instance, **kwargs):
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # TODO: We still have not finalized the permissions required for users when the muo is marked as inappropriate
    # TODO: Once finalized, just replace it in codename__in field below
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(profile__notify_muo_inappropriate=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm))
    emails = [user.email for user in users]
    subject = constants.MUO_INAPPROPRIATE_SUBJECT
    action = constants.INAPPROPRIATE
    generate_bulk_email(instance, subject, action, emails)


# TODO: All other reviewers should be notified - need to handle that
# Handled for this case
@receiver(muo_submitted_for_review)
def on_muo_submitted_for_review(sender,instance, **kwargs):
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(profile__notify_muo_submitted_for_review=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm))
    emails = [user.email for user in users]
    subject = constants.MUO_SUBMITTED_FOR_REVIEW_SUBJECT
    action = constants.SUBMITTED
    generate_bulk_email(instance, subject, action, emails)


# TODO: All reviewers should be notified - need to handle that
@receiver(custom_muo_created)
def on_custom_muo_created(sender,instance,**kwargs):
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # TODO: We still have not finalized the permissions required for users when the custom muo gets created
    # TODO: Once finalized, just replace it in codename__in field below
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(profile__notify_custom_muo_created=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm))
    emails = [user.email for user in users]
    subject = constants.CUSTOM_MUO_CREATED_SUBJECT
    action = constants.CREATED
    generate_bulk_email(instance, subject, action, emails)


# All other reviewers should be notified and also the created_by user - need to handle that
@receiver(custom_muo_promoted_generic)
def on_custom_muo_promoted_generic(sender,instance,**kwargs):
    if instance.created_by.profile.notify_custom_muo_promoted_as_generic:
        subject = constants.CUSTOM_MUO_PROMOTED_SUBJECT
        action = constants.PROMOTED
        generate_email(instance, subject, action)

    # Send an email to all the reviewers who wants to be notified when the custom muo gets promoted as generic
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # TODO: We still have not finalized the permissions required for users when the custom muo gets promoted as generic
    # TODO: Once finalized, just replace it in codename__in field below
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(profile__notify_custom_muo_promoted_as_generic=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm))
    emails = [user.email for user in users]
    subject = constants.CUSTOM_MUO_PROMOTED_SUBJECT
    action = constants.PROMOTED
    generate_bulk_email(instance, subject, action, emails)

"""
This method is called when we have to send the email after fixing all the parameters
"""
def generate_email(instance, subject, action):
    user = instance.created_by
    muo_name = instance.name
    send_mail(subject, get_template('emailer/muo_action.html').render(
        Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': action,
        })
    ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

"""
This method is called when we have to send bulk email to many recipients
"""
def generate_bulk_email(instance, subject, action, emails):
    send_mail(subject, get_template('emailer/muo_action_bulk.html').render(
        Context({
            'muo_name': instance.muo_name,
            'action': action,
            })
        ), constants.SENDER_EMAIL, emails, fail_silently=True)













