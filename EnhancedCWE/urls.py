"""EnhancedCWE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from base import admin as base_admin
from register.forms import MyAuthenticationForm
from register import views
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


urlpatterns = [

    url(r'^admin/', include(base_admin.admin_site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url('^registration/', include('registration.urls')),
    url(r'restapi/', include('rest_api.urls')),
]


