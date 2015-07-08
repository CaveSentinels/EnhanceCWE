from django.views.generic.base import TemplateView

class PendingApprovalView(TemplateView):
    template_name = 'register/pending_approval.html'

pending_approval = PendingApprovalView.as_view()