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
    user_object = context.get('user')

    ctx.update({
        'show_save_and_add_another': False,
        'show_save_and_continue': False,
        "show_approve": user_object.has_perm('muo.can_approve') and
                        model_object and model_object.status == 'in_review',
        'show_reject': user_object.has_perm('muo.can_reject') and
                       model_object and model_object.status in ('in_review', 'approved'),
        'show_submit_for_review': model_object and model_object.status == 'draft',
        'show_edit': model_object and (model_object.status == 'in_review' or model_object.status == 'rejected'),
    })

    return ctx
