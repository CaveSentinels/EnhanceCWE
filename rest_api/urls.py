from django.conf.urls import url
from rest_api import views

urlpatterns = [
    url(r'^cwe/text_related$', views.CWERelatedList.as_view(), name="restapi_CWETextRelated"),
    url(r'^cwe/all$', views.CWEAllList.as_view(), name="restapi_CWEAll"),
    url(r'^misuse_case/cwe_related$', views.MisuseCaseRelated.as_view(), name="restapi_MisuseCase_CWERelated"),
    url(r'^use_case/misuse_case_related$', views.UseCaseRelated.as_view(), name="restapi_UseCase_MisuseCaseRelated"),
    url(r'^custom_muo/save$', views.SaveCustomMUO.as_view(), name="restapi_CustomMUO_Create"),
]
