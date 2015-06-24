'''
This file will contain all the custom template tags for the
MUO app.
'''

from django.contrib.admin.templatetags.admin_modify import *
from base.templatetags.admin_modify import submit_row as original_submit_row
from django import template


register = template.Library()


@register.inclusion_tag('admin/muo/muocontainer/muo_submit_line.html', takes_context=True)
def muo_submit_row(context):
    ctx = original_submit_row(context)

    model_object = ctx.get('original')
    print model_object.isCustom
    user_object = context.get('user')

    ctx.update({
        # Do not show save and add another button
        'show_save_and_add_another': False,

        # Show save and delete buttons only if the muo is created by the current user
        'show_save_and_continue': user_object == model_object.created_by,
        'show_save_as_new': user_object == model_object.created_by,
        'show_save': user_object == model_object.created_by,
        'show_delete_link': user_object == model_object.created_by,

        # Show submit for review button only to the creator of the muo and if its in draft state
        'show_submit_for_review': user_object == model_object.created_by and
                                  model_object and model_object.status == 'draft',

        # Show edit button only to the creator of the muo and if its either in in_review or rejected state
        'show_edit': user_object == model_object.created_by and
                     model_object and
                     (model_object.status == 'in_review' or model_object.status == 'rejected'),

        # Show approve button only to the user if he/she has the can_approve permission and the state of
        # muo is in in_review
        'show_approve': user_object.has_perm('muo.can_approve') and
                        model_object and
                        model_object.status == 'in_review',

        # Show reject button only to the user if he/she has the can_reject permission and the state of the
        # muo is in in_review or approved state
        'show_reject': user_object.has_perm('muo.can_reject') and
                       model_object and
                       model_object.status in ('in_review', 'approved'),

        # Show promote button only to the user if he/she has can_approve permission and the muo is custom
        # muo and its in draft state
        'show_promote': user_object.has_perm('muo.can_approve') and
                        model_object and
                        model_object.isCustom == True and
                        model_object.status == 'draft'
    })

    return ctx
