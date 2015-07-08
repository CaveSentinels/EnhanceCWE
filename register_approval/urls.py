from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^', views.pending_approval, name="account_pending_approval"),
]
