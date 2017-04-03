from django.conf.urls import url

from fiveapp import views

urlpatterns = [
    url(r'^user$', views.user, name='POST User'),
    url(r'^next_chat_time$', views.next_chat_time, name='get chat details'),
    url(r'^get_session$', views.get_session, name='get session'),
]
