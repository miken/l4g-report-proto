from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.SurveyList.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.SurveyDetail.as_view(), name='detail'),
]
