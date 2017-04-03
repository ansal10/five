import json
from datetime import timedelta, datetime

import pytz
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.
from opentok import OpenTok
from rest_framework.decorators import api_view

from fiveapp.models import Users, Chats, Opentok
from fiveapp.utils import now


def error_response(msg, status=400):
    return JsonResponse({"error": msg}, status=status)

SECONDS = 300
@api_view(['POST'])
def user(request):
    data = json.loads(request.body)
    for key in ['facebook_id', 'firebase_id', 'fb_data']:
        if key not in data or data[key] == None:
            return error_response("%s Key is not empty" % key)

    firebase_id = data['firebase_id']
    facebook_id = data['facebook_id']
    fb_data = data['fb_data']

    new_user = False
    users = Users.objects.filter(firebase_id=firebase_id, facebook_id=facebook_id)
    if users.exists():
        user = users.first()
    else:
        user = Users(firebase_id=firebase_id, facebook_id=facebook_id, fb_data=fb_data)
        new_user = True

    user.fb_data = fb_data
    user.save()

    return JsonResponse({
        "new_signup": new_user,
        "user_uuid": user.user_uuid
    })


@api_view(['POST'])
def get_chat_time(request):
    data = json.loads(request.body)
    for key in ['user_uuid']:
        if key not in data or data[key] is None:
            return error_response("%s Key is not empty" % key)

    user_uuid = data['user_uuid']
    chat = get_chat_for_user(user_uuid)

    if chat is None:
        return error_response("You don't have any chats Scheduled")

    res_data = {
        "chat_time": chat.chat_time
    }
    return JsonResponse(res_data)




@api_view(['POST'])
def get_session(request):
    data = json.loads(request.body)
    for key in ['user_uuid']:
        if key not in data or data[key] is None:
            return error_response("%s Key is not empty" % key)

    chat = get_chat_for_user(user_uuid=data['user_uuid'])
    time_diff = abs(chat.chat_time - now())
    time_diff = (time_diff.days*24*60*60) + time_diff.seconds
    if chat is None or time_diff >= SECONDS:
        return error_response("You don't have any chats Scheduled")

    if chat.opentok_session_id is None:
        opentok_session_id = generate_opentok_session()
        chat.opentok_session_id = opentok_session_id
        chat.save()
    else:
        opentok_session_id = chat.opentok_session_id

    return JsonResponse({"opentok_session_id": opentok_session_id})


def get_chat_for_user(user_uuid):
    user = Users.objects.filter(user_uuid=user_uuid).first()
    from_time = now() - timedelta(0, SECONDS)
    chats = Chats.objects.filter(Q(Q(userA=user) | Q(userB=user)), chat_time__gte=from_time)

    if not chats.exists():
        return None
    else :
        return chats.first()



def generate_opentok_session():
    optok = Opentok.objects.filter(mode='development').first()
    opentok = OpenTok(optok.api_key, optok.api_secret)
    session = opentok.create_session()
    return session.session_id

