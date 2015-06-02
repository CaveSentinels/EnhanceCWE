from django.contrib import admin
from django.contrib.admin import options
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.utils import (get_deleted_objects, unquote)

from django.core.exceptions import PermissionDenied

from django.db import router, transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import SimpleTemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect


IS_POPUP_VAR = options.IS_POPUP_VAR
TO_FIELD_VAR = options.TO_FIELD_VAR
HORIZONTAL, VERTICAL = options.HORIZONTAL, options.VERTICAL

csrf_protect_m = method_decorator(csrf_protect)


class BaseAdmin(admin.ModelAdmin):
    """
    This is a base ModelAdmin that provides basic common features that are
    necessary to most admin models.
    Interested models should inherit from this class instead of models.Model
    """

    @csrf_protect_m
    @transaction.atomic
    def delete_view(self, request, object_id, extra_context=None):
        """
        This method overrides the 'delete' admin view.
        Changes include handling exceptions raised while deleting a model and
        displaying the exception message to the user in a readable format instead of
        showing the exception page to the user
        """
        opts = self.model._meta
        app_label = opts.app_label

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_delete_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(
                _('%(name)s object with primary key %(key)r does not exist.') %
                {'name': force_text(opts.verbose_name), 'key': escape(object_id)}
            )

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (deleted_objects, model_count, perms_needed, protected) = get_deleted_objects(
            [obj], opts, request.user, self.admin_site, using)

        if request.POST:  # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = force_text(obj)
            attr = str(to_field) if to_field else opts.pk.attname
            obj_id = obj.serializable_value(attr)

            # start: base changes
            try:
                self.delete_model(request, obj)
            except Exception as e:
                return self.response_delete(request, obj_display, obj_id,
                                            msg=e.message, msg_type=messages.ERROR)

            self.log_deletion(request, obj, obj_display)
            # end: base changes

            return self.response_delete(request, obj_display, obj_id)

        object_name = force_text(opts.verbose_name)

        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": object_name}
        else:
            title = _("Are you sure?")

        context = dict(
            self.admin_site.each_context(request),
            title=title,
            object_name=object_name,
            object=obj,
            deleted_objects=deleted_objects,
            model_count=dict(model_count).items(),
            perms_lacking=perms_needed,
            protected=protected,
            opts=opts,
            app_label=app_label,
            preserved_filters=self.get_preserved_filters(request),
            is_popup=(IS_POPUP_VAR in request.POST or
                      IS_POPUP_VAR in request.GET),
            to_field=to_field,
        )
        context.update(extra_context or {})

        return self.render_delete_form(request, context)

    def response_delete(self, request, obj_display, obj_id,
                        msg=None, msg_type=messages.SUCCESS):
        """
        This overrides the HttpResponse for the delete_view stage.
        It adds new option variables:
        msg: the message to display to the user after deletion request
        msg_type: the message type (SUCCESS, ERROR, WARNING)

        """

        opts = self.model._meta

        if IS_POPUP_VAR in request.POST:
            return SimpleTemplateResponse('admin/popup_response.html', {
                'action': 'delete',
                'value': escape(obj_id),
            })

        # If msg is not defined, then respond with the default delete message
        if not msg:
            msg = _('The %(name)s "%(obj)s" was deleted successfully.') % {
                'name': force_text(opts.verbose_name),
                'obj': force_text(obj_display),
            }

        self.message_user(request, msg, msg_type)

        if self.has_change_permission(request, None):
            post_url = reverse('admin:%s_%s_changelist' %
                               (opts.app_label, opts.model_name),
                               current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url
            )
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)