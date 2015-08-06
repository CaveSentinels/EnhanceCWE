import threading
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django_comments.signals import comment_was_posted
from muo.models import *
from muo.signals import *
import constants

SENDER_EMAIL = getattr(settings, 'SENDER_EMAIL', '')


"""
All of these methods are the handlers for the signals defined in signals.py in the
MUO Application.
They create the email body by fetching the parameters and send the email
"""

# This method will send an email when an MUO gets accepted
@receiver(muo_accepted)
def on_muo_accepted(sender, instance, **kwargs):
    if instance.created_by and instance.created_by.mailer_profile.notify_muo_accepted:
        subject = constants.MUO_ACCEPTED_SUBJECT
        action = constants.ACCEPTED
        notify_owner(instance, subject, action)

# This method will send an email when an MUO gets rejected
@receiver(muo_rejected)
def on_muo_rejected(sender, instance, **kwargs):
    if instance.created_by and instance.created_by.mailer_profile.notify_muo_rejected:
        subject = constants.MUO_REJECTED_SUBJECT
        action = constants.REJECTED
        notify_owner(instance, subject, action)


# This method will send an email when the MUO is commented upon
@receiver(comment_was_posted)
def on_muo_commented(sender, comment, request, **kwargs):
    if comment.content_type == ContentType.objects.get_for_model(UseCase):
        instance = comment.content_object
        if instance.created_by and instance.created_by.mailer_profile.notify_muo_commented:
            subject = constants.MUO_COMMENTED_SUBJECT
            action = constants.COMMENTED
            notify_owner(instance, subject, action)


@receiver(post_save, sender=IssueReport)
def on_muo_inappropriate(sender, instance, created=False, **kwargs):
    if created:
        muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
        # First filter the permission which has to be checked from the list of permission in the muo_container
        perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
        # The user might have the permission either as a user or in a group of which he is a part, so check both
        users = User.objects.filter(mailer_profile__notify_muo_inappropriate=True)\
                            .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm)).distinct()
        emails = [user.email for user in users]
        subject = constants.MUO_INAPPROPRIATE_SUBJECT
        action = constants.INAPPROPRIATE
        notify_reviewers(instance.usecase.muo_container, subject, action, emails)


# TODO: All other reviewers should be notified - need to handle that
# Handled for this case
@receiver(muo_submitted_for_review)
def on_muo_submitted_for_review(sender,instance, **kwargs):
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(mailer_profile__notify_muo_submitted_for_review=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm)).distinct()
    emails = [user.email for user in users]
    subject = constants.MUO_SUBMITTED_FOR_REVIEW_SUBJECT
    action = constants.SUBMITTED
    notify_reviewers(instance, subject, action, emails)


# TODO: All reviewers should be notified - need to handle that
@receiver(custom_muo_created)
def on_custom_muo_created(sender,instance,**kwargs):
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # TODO: We still have not finalized the permissions required for users when the custom muo gets created
    # TODO: Once finalized, just replace it in codename__in field below
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(mailer_profile__notify_custom_muo_created=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm)).distinct()
    emails = [user.email for user in users]
    subject = constants.CUSTOM_MUO_CREATED_SUBJECT
    action = constants.CREATED
    notify_reviewers(instance, subject, action, emails)


# All other reviewers should be notified and also the created_by user - need to handle that
@receiver(custom_muo_promoted_generic)
def on_custom_muo_promoted_generic(sender,instance,**kwargs):
    if instance.created_by and instance.created_by.mailer_profile.notify_custom_muo_promoted_as_generic:
        subject = constants.CUSTOM_MUO_PROMOTED_SUBJECT
        action = constants.PROMOTED
        notify_owner(instance, subject, action)

    # Send an email to all the reviewers who wants to be notified when the custom muo gets promoted as generic
    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    # TODO: We still have not finalized the permissions required for users when the custom muo gets promoted as generic
    # TODO: Once finalized, just replace it in codename__in field below
    # First filter the permission which has to be checked from the list of permission in the muo_container
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = muo_container_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(mailer_profile__notify_custom_muo_promoted_as_generic=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm)).distinct()
    emails = [user.email for user in users]
    subject = constants.CUSTOM_MUO_PROMOTED_SUBJECT
    action = constants.PROMOTED
    notify_reviewers(instance, subject, action, emails)



def notify_owner(instance, subject, action):
    thread = threading.Thread(target=_notify_owner, args=(instance, subject, action))
    thread.start()

def _notify_owner(instance, subject, action):
    """
    This method is called when we have to send the email after fixing all the parameters
    """
    user = instance.created_by
    muo_name = instance.name
    send_mail(subject, get_template('mailer/muo_action.html').render(
        Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': action,
        })
    ), SENDER_EMAIL, [user.email], fail_silently=True)



def notify_reviewers(instance, subject, action, emails):
    thread = threading.Thread(target=_notify_reviewers, args=(instance, subject, action, emails))
    thread.start()

def _notify_reviewers(instance, subject, action, emails):
    """
    This method is called when we have to send bulk email to many recipients
    """
    if emails:
        send_mail(subject, get_template('mailer/muo_action_bulk.html').render(
            Context({
                'muo_name': instance.name,
                'action': action,
                })
            ), SENDER_EMAIL, emails, fail_silently=True)
