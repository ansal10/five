import json
from datetime import timedelta, datetime

import pytz
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.
from opentok import OpenTok, opentok
from rest_framework.decorators import api_view

from fiveapp import utils
from fiveapp.models import Users, Chats, Opentok
from fiveapp.utils import now


def error_response(msg, status=400):
    return JsonResponse({"error": msg}, status=status)


SECONDS = 300


@api_view(['POST'])
def user(request):
    data = json.loads(request.body)
    # username, password = utils.retrieve_username_password_from_authorization(request)
    for key in ['firebase_user_id', 'fb_data']:
        if key not in data or data[key] == None:
            return error_response("%s Key is not empty" % key)

    firebase_user_id = data['firebase_user_id']
    facebook_id = data.get('facebook_id', None)
    fb_data = data['fb_data']

    new_user = False
    users = Users.objects.filter(firebase_user_id=firebase_user_id, facebook_id=facebook_id)
    if users.exists():
        user = users.first()
    else:
        user = Users(firebase_user_id=firebase_user_id, facebook_id=facebook_id, fb_data=fb_data)
        new_user = True

    user.fb_data = fb_data
    user.save()

    json_res = JsonResponse({
        "new_signup": new_user,
        "user_uuid": user.user_uuid
    })
    return json_res


@api_view(['POST'])
def next_chat_time(request):
    user_uuid, password = utils.retrieve_username_password_from_authorization(request)
    if not Users.objects.filter(user_uuid=user_uuid).exists():
        return error_response("Unauthorized Access", 401)

    chat = get_chat_for_user(user_uuid)

    if chat is None:
        return error_response("You don't have any chats Scheduled")

    res_data = {
        "chat_time": chat.chat_time
    }
    return JsonResponse(res_data)


@api_view(['POST'])
def get_session(request):
    user_uuid, password = utils.retrieve_username_password_from_authorization(request)
    if not Users.objects.filter(user_uuid=user_uuid).exists():
        return error_response("Unauthorized Access", 401)

    chat = get_chat_for_user(user_uuid=user_uuid)
    time_diff = abs(chat.chat_time - now())
    time_diff = (time_diff.days * 24 * 60 * 60) + time_diff.seconds
    if chat is None or time_diff >= SECONDS:
        return error_response("You don't have any chats Scheduled")

    if not chat.opentok_session_id:
        opentok_session_id = generate_opentok_session()
        chat.opentok_session_id = opentok_session_id
        chat.save()
    else:
        opentok_session_id = chat.opentok_session_id

    token = generate_opentok_token(opentok_session_id)
    api_key = Opentok.get_api_key()
    session_id = opentok_session_id

    data = {
        "token": token,
        "sessionId": session_id,
        "apiKey": api_key
    }

    return JsonResponse(data)


def get_chat_for_user(user_uuid):
    user = Users.objects.filter(user_uuid=user_uuid).first()
    from_time = now() - timedelta(0, SECONDS)
    chats = Chats.objects.filter(Q(Q(userA=user) | Q(userB=user)), chat_time__gte=from_time)

    if not chats.exists():
        return None
    else:
        return chats.first()


def generate_opentok_session():
    optok = Opentok.objects.filter(mode='development').first()
    opentok = OpenTok(optok.api_key, optok.api_secret)
    session = opentok.create_session()
    return session.session_id


def generate_opentok_token(session_id):
    optok = Opentok.objects.filter(mode='development').first()
    opentok = OpenTok(optok.api_key, optok.api_secret)
    token = opentok.generate_token(session_id)
    return token
