from django.conf.urls import url

from fiveapp import apis, views

urlpatterns = [
    url(r'^user$', view=apis.user, name='POST User'),
    url(r'^next_chat$', view=apis.next_chat, name='get chat details'),
    url(r'^get_session$', view=apis.get_session, name='get session'),
    url(r'^update_user_details$', view=apis.update_user_details, name='update user details'),
    url(r'^ratings$', view=apis.update_ratings, name='Update Ratings'),
    url(r'^get_filters$', view=apis.get_filters, name='Retrieve Filters'),
    url(r'^update_chats$', view=apis.update_chats, name='New Chat'),
    url(r'^retrieve_users_and_chats$', view=views.retrieve_users_and_chats, name='Retrive all users and chats'),
    url(r'^login$', view=views.authenticate_user, name='Login User'),
    url(r'^test$', view=apis.test, name='Test Server')
]
