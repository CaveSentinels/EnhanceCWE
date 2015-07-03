from fluent_comments import urls as fluent_urls
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^delete/(\d+)/$', views.delete, name='comments-delete'),
] + fluent_urls.urlpatterns
