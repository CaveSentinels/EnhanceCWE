from django.dispatch import receiver
from muo.signals import *
from django.core.mail import send_mail
# get_template is what we need for loading up the template for parsing.
from django.template.loader import get_template
from django.template import Context
from user_profile.models import *
from django.contrib.auth.models import User
import constants


"""
This method is the handler for signal muo_accepted
It will create the email body by using the parameters and send the email
"""
@receiver(muo_accepted)
def on_muo_accepted(sender, instance, **kwargs):
    if UserProfile.notify_when_muo_accepted:
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
    if UserProfile.notify_when_muo_rejected:
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
    if UserProfile.notify_when_muo_voted_up:
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
    if UserProfile.notify_when_muo_voted_down:
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
    if UserProfile.notify_when_muo_commented:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_COMMENTED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
                'full_name': user.get_full_name() or user.username,
                'muo_name': muo_name,
                'action': constants.COMMENTED,
                })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)


@receiver(muo_duplicate)
def on_muo_duplicate(sender,instance, **kwargs):
    if UserProfile.notify_when_muo_duplicate:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_DUPLICATE_SUBJECT,get_template('emailer/muo_action.html').render(
            Context({
            'full_name':user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.DUPLICATE,

        })), constants.SENDER_EMAIL, [user.email], fail_silently=True)

@receiver(muo_inappropriate)
def on_muo_inappropriate(sender,instance, **kwargs):
    if UserProfile.notify_when_muo_inappropriate:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_INAPPROPRIATE_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.INAPPROPRIATE,

            })
         ), constants.SENDER_EMAIL, [user.email], fail_silently=True)




@receiver(muo_submitted_for_review)
def on_muo_submitted_for_review(sender,instance, **kwargs):
    if MUONotification.notify_when_muo_submitted_for_review:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.MUO_SUBMITTED_FOR_REVIEW_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.SUBMITTED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

@receiver(custom_muo_created)
def on_custom_muo_created(sender,instance,**kwargs):
    if MUONotification.notify_when_custom_muo_created:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.CUSTOM_MUO_CREATED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.CREATED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)

@receiver(custom_muo_promoted_generic)
def on_custom_muo_promoted_generic(sender,instance,**kwargs):
    if MUONotification.notify_when_custom_muo_promoted_as_generic:
        user = instance.created_by
        muo_name = instance.name
        send_mail(constants.CUSTOM_MUO_PROMOTED_SUBJECT, get_template('emailer/muo_action.html').render(
            Context({
            'full_name': user.get_full_name() or user.username,
            'muo_name': muo_name,
            'action': constants.PROMOTED,
            })
        ), constants.SENDER_EMAIL, [user.email], fail_silently=True)











