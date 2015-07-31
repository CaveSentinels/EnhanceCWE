from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_cwes/$', views.get_cwes, name='get_cwes'),
    url(r'^get_misusecases/$', views.get_misusecases, name='get_misusecases'),
    url(r'^get_usecases/$', views.get_usecases, name='get_usecases'),
    url(r'^create_issue_report/$', views.create_issue_report, name='create_issue_report'),
    url(r'^process_issue_report/$', views.process_issue_report, name='process_issue_report'),
]