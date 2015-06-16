from django.conf.urls import url
from rest_api import views

# The signed/unsigned integers. The source of regex is http://stackoverflow.com/a/16774198/630364
REGEX_SIGNED_UNSIGNED_INTEGER = r'[+-]?(?<!\.)\b[0-9]+\b(?!\.[0-9])'

urlpatterns = [
    url(r'^cwe/text_related/(?P<text>.+)/$', views.CWERelatedList.as_view()),
    url(r'^cwe/all/$', views.CWEAllList.as_view()),
    url(r'^cwe/all/(?P<offset>' + REGEX_SIGNED_UNSIGNED_INTEGER + r')/$', views.CWEAllList.as_view()),
    url(r'^cwe/all/(?P<offset>' + REGEX_SIGNED_UNSIGNED_INTEGER + r')/(?P<max_return>' + REGEX_SIGNED_UNSIGNED_INTEGER + r')/$', views.CWEAllList.as_view()),
    url(r'^misuse_case/cwe_related$', views.MisuseCaseRelated.as_view()),
    url(r'^use_case/misuse_case_related$', views.UseCaseRelated.as_view()),
]