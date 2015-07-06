'''
+This file will contain all the custom template tags for the
+Invitation app.
+'''

from django.contrib.admin.templatetags.admin_modify import *
from base.templatetags.admin_modify import submit_row as original_submit_row
from django import template

register = template.Library()


@register.inclusion_tag('admin/invitation/invitation_submit_line.html', takes_context=True)
def invitation_submit_row(context):
    ctx = original_submit_row(context)

    model_object = ctx.get('original')
    user_object = context.get('user')
    ctx.update({
        # Show investigate button only when the issue is in open state and the user has approve & reject perm
        'show_send_invitation': True,

    })

    return ctx
