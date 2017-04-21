import json

from django.contrib.auth import authenticate, login
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

from fiveapp.apis import error_response
from fiveapp.models import Opentok, Users, Chats
from fiveapp.utils import DateTimeEncoder, retrieve_username_password_from_authorization


# def chat_panel(request):
#     if not request.user.is_authenticated:
#         return error_response('Unauthorized Access', 401)
#
#     apikey = request.GET.get('api_key', None)
#     api_key = Opentok.get_api_key()
#     users = Users.objects.values('user_uuid', 'fb_link', 'fb_profile_data', 'name', 'email').all()
#     chats = Chats.objects.values('id', 'userA__user_uuid', 'userB__user_uuid', 'chat_time').all()
#     for chat in chats:
#         chat['chat_time'] = chat['chat_time'].__str__()
#
#     data = {
#         "users": [user for user in users],
#         "chats": [chat for chat in chats]
#     }
#     return render(request, 'chat_panel.html', {"data": data})


def retrieve_users_and_chats(request):
    username, password = retrieve_username_password_from_authorization(request)
    if username != Opentok.get_api_key():
        return error_response('Unauthorized Access', 401)

    users = Users.objects.values('user_uuid', 'fb_link', 'fb_profile_data', 'name', 'email', 'filters', 'timezone').all()
    chats = Chats.objects.values('id', 'userA__user_uuid', 'userB__user_uuid', 'chat_time', 'userA__name', 'userA__email', 'userB__name', 'userB__name').all()
    for chat in chats:
        chat['chat_time'] = chat['chat_time'].__str__()

    data = {
        "users": [user for user in users],
        "chats": [chat for chat in chats]
    }
    return JsonResponse({
        "data":data
    })

@api_view(['POST'])
def authenticate_user(request):
    data = json.loads(request.body)
    username = data['username']
    password = data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"status": "ok"})
    else:
        return error_response("invalid cred", 401)
