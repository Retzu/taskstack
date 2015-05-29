from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'groups/(?P<pk>[0-9]+)', views.GroupDetail.as_view()),
    url(r'groups', views.GroupList.as_view()),
]