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
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_ACCEPTED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
                'full_name': user.get_full_name() or user.username,
                'muo_name': muo_name,
                'action': constants.ACCEPTED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)


# This method will send an email when an MUO gets rejected
@receiver(muo_rejected)
def on_muo_rejected(sender,instance,**kwargs):
    if instance.created_by.profile.notify_muo_rejected:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_REJECTED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
                'full_name': user.get_full_name() or user.username,
                'muo_name': muo_name,
                'action': constants.REJECTED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

# This method will send an email when the MUO is voted up by any user
@receiver(muo_voted_up)
def on_muo_voted_up(sender, instance, **kwargs):
    if instance.created_by.profile.notify_muo_voted_up:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_VOTED_UP_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
                'full_name': user.get_full_name() or user.username,
                'muo_name': muo_name,
                'action': constants.VOTEDUP,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

# This method will send an email when the MUO is voted down by any user
@receiver(muo_voted_down)
def on_muo_voted_down(sender, instance, **kwargs):
    if instance.created_by.profile.notify_muo_voted_down:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_VOTED_DOWN_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
                'full_name': user.get_full_name() or user.username,
                'muo_name': muo_name,
                'action': constants.VOTEDDOWN,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)


# This method will send an email when the MUO is commented upon
@receiver(muo_commented)
def on_muo_commented(sender, instance,**kwargs):
    if instance.created_by.profile.notify_muo_commented:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_COMMENTED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
                'full_name': user.get_full_name() or user.username,
                'muo_name': muo_name,
                'action': constants.COMMENTED,
                })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

# TODO:More people would want to be notified not just the writer- need to handle that
@receiver(muo_duplicate)
def on_muo_duplicate(sender,instance, **kwargs):
    if instance.created_by.profile.notify_muo_duplicate:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_DUPLICATE_SUBJECT,get_template('emailer/muo_action.html').render(
            Context({
            'full_name':user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.DUPLICATE,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

# TODO: All other reviewers should be notified and not just the created_by user - need to handle that
@receiver(muo_inappropriate)
def on_muo_inappropriate(sender,instance, **kwargs):
    if instance.created_by.profile.notify_muo_inappropriate:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_INAPPROPRIATE_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.INAPPROPRIATE,
            })
         ), constants.SENDER_EMAIL, [user.email], fail_silently=True)


# TODO: All other reviewers should be notified and not just the created_by user - need to handle that
@receiver(muo_submitted_for_review)
def on_muo_submitted_for_review(sender,instance, **kwargs):

    muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'),
                                  content_type = muo_container_type)

    users = User.objects.filter(profile__notify_muo_submitted_for_review=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm))
    
    user = instance.created_by
    muo_name = instance.name
    send_mail(constants.MUO_SUBMITTED_FOR_REVIEW_SUBJECT, get_template('emailer/muo_action.html').render(
        Context({
        'full_name': user.get_full_name() or user.username,
        'muo_name': muo_name,
        'action': constants.SUBMITTED,
        })
    ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

# TODO: All other reviewers should be notified and not just the created_by user - need to handle that
@receiver(custom_muo_created)
def on_custom_muo_created(sender,instance,**kwargs):
    if instance.created_by.profile.notify_custom_muo_created:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.CUSTOM_MUO_CREATED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.CREATED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

# TODO: All other reviewers should be notified and not just the created_by user - need to handle that
@receiver(custom_muo_promoted_generic)
def on_custom_muo_promoted_generic(sender,instance,**kwargs):
    if instance.created_by.profile.notify_custom_muo_promoted_as_generic:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.CUSTOM_MUO_PROMOTED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.PROMOTED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)











