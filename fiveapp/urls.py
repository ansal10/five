from django.conf.urls import url

from fiveapp import views

urlpatterns = [
    url(r'^user$', view=views.user, name='POST User'),
    url(r'^next_chat$', view=views.next_chat, name='get chat details'),
    url(r'^get_session$', view=views.get_session, name='get session'),
    url(r'^update_user_details', view=views.update_user_details, name='update user details')
]
