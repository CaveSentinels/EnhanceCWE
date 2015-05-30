'''
This file will contain all the custom template tags for the
MUO app.
'''

from django.contrib.admin.templatetags.admin_modify import *
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row
from django import template


register = template.Library()


@register.inclusion_tag('admin/muo/muocontainer/muo_submit_line.html', takes_context=True)
def muo_submit_row(context):
    ctx = original_submit_row(context)

    model_object = ctx.get('original')

    ctx.update({
        'show_save_and_add_another': False,
        'show_save_and_continue': False,
        'show_save': False,
        'show_approve': model_object and model_object.status == 'in_review',
        'show_reject': model_object and
                       (model_object.status == 'in_review' or
                        (model_object.status == 'approved' and model_object.published_status == 'unpublished')),
        'show_submit_for_review': model_object and model_object.status == 'draft',
        'show_edit': model_object and (model_object.status == 'in_review' or model_object.status == 'rejected'),
        'show_publish': model_object and
                        (model_object.status == 'approved' and model_object.published_status == 'unpublished'),
        'show_unpublish': model_object and
                          (model_object.status == 'approved' and model_object.published_status == 'published')
    })

    return ctx
