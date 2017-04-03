from django.conf.urls import url

from fiveapp import views

urlpatterns = [
    url(r'^user$', views.user, name='POST User'),
    url(r'^get_chat_details$', views.get_chat_time, name='get chat details'),
    url(r'^get_session$', views.get_session, name='get session'),
]
