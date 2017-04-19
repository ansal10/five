import json
from datetime import timedelta

import logging
from django.db.models import Q
from django.http import JsonResponse
from opentok import OpenTok, MediaModes, ArchiveModes
from rest_framework.decorators import api_view

from config import SECONDS, MIN_BUILD_VERSION_FOR_FORCE_UPDATE
from fiveapp import utils
from utilities.gcm_notification import GCMNotificaiton
from utils import now, retrieve_username_password_from_authorization
from fiveapp.models import Users, Chats, Opentok
from fiveapp.utils import now, update_user_fb_profile_data

logger = logging.getLogger('fiveapp')


def error_response(msg, status=400):
    return JsonResponse({"error": msg}, status=status)


TOTAL_RATING_COUNT = 'total_rating_counts'


@api_view(['POST'])
def user(request):
    try:
        data = json.loads(request.body)
        build_version = float(data['build_version'])

        if data.get('firebase_user_id', None) is None:
            return JsonResponse({
                "force_update": True if build_version < MIN_BUILD_VERSION_FOR_FORCE_UPDATE else False
            })
        for key in ['firebase_user_id', 'build_version']:
            if key not in data or data[key] == None:
                return error_response("%s Key is empty" % key)

        firebase_user_id = data['firebase_user_id']
        facebook_id = data.get('facebook_id', None)
        fb_data = data.get('fb_data', None)
        fcm_token = data.get('fcm_token', None)
        app_id = data.get('app_id', None)

        force_update = True if build_version < MIN_BUILD_VERSION_FOR_FORCE_UPDATE else False

        new_user = False
        users = Users.objects.filter(firebase_user_id=firebase_user_id, facebook_id=facebook_id)
        if users.exists():
            user = users.first()
        else:
            user = Users(firebase_user_id=firebase_user_id, facebook_id=facebook_id, fb_data=fb_data)
            new_user = True
        user = update_user_fb_profile_data(user) if not user.fb_profile_data else user

        # set conditional data
        user.fb_data = fb_data if fb_data else user.fb_data
        user.fcm_token = fcm_token if fcm_token else user.fcm_token
        user.app_id = app_id if app_id else user.app_id

        user.save()

        json_res = JsonResponse({
            "new_signup": new_user,
            "user_uuid": user.user_uuid,
            "gender": user.gender,
            "filters": user.filters if user.filters else None,
            "force_update": force_update
        })
        return json_res
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


@api_view(['POST'])
def update_user_details(request):
    try:
        user_uuid, password = utils.retrieve_username_password_from_authorization(request)
        if not Users.objects.filter(user_uuid=user_uuid).exists():
            return error_response("Unauthorized Access", 401)
        user = Users.objects.filter(user_uuid=user_uuid).first()
        data = json.loads(request.body)
        fb_data = data.get('fb_data', None)
        filters = data.get('filters', None)
        user.fb_data = fb_data if fb_data else user.fb_data
        user.filters = filters if filters else user.filters
        user.save()

        return JsonResponse({
            "user_uuid": user.user_uuid
        })
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


@api_view(['POST'])
def next_chat(request):
    try:
        user_uuid, password = utils.retrieve_username_password_from_authorization(request)
        if not Users.objects.filter(user_uuid=user_uuid).exists():
            return error_response("Unauthorized Access", 401)

        chat, on_going_chat = get_current_or_next_chat_for_user(user_uuid)

        if chat is None or chat.rating_by_userA or chat.rating_by_userB:
            return JsonResponse({"chat": None})

        other_user = chat.userA if chat.userA.user_uuid != user_uuid else chat.userB
        time_diff = abs(chat.chat_time - now())
        time_diff = (time_diff.days * 24 * 60 * 60) + time_diff.seconds if not on_going_chat else 0
        res_data = {
            "chat": {
                "seconds_left_for_chat_start": time_diff,
                "chat_start_time": chat.chat_time,
                "chat_end_time": chat.chat_time + timedelta(0, SECONDS),
                "current_time": now().isoformat(),
                "user": {
                    "gender": other_user.gender,
                    "fcm_token":other_user.fcm_token
                }
            }
        }
        if time_diff <= 5:
            if not chat.opentok_session_id:
                opentok_session_id = generate_opentok_session()
                chat.opentok_session_id = opentok_session_id
                chat.save()

            token, api_key, session_id = get_opentok_details(chat.opentok_session_id)
            res_data['chat']['session_data'] = {
                "token": token,
                "sessionId": session_id,
                "apiKey": api_key
            }
        return JsonResponse(res_data)
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


@api_view(['POST'])
def get_session(request):
    try:
        user_uuid, password = utils.retrieve_username_password_from_authorization(request)
        if not Users.objects.filter(user_uuid=user_uuid).exists():
            return error_response("Unauthorized Access", 401)

        user = Users.objects.filter(user_uuid=user_uuid).first()
        chat, on_going_chat = get_current_or_next_chat_for_user(user_uuid=user_uuid)
        time_diff = abs(chat.chat_time - now())
        time_diff = (time_diff.days * 24 * 60 * 60) + time_diff.seconds
        if chat is None or time_diff >= SECONDS:
            return JsonResponse({"session": None})

        if not chat.opentok_session_id:
            opentok_session_id = generate_opentok_session()
            chat.opentok_session_id = opentok_session_id
            chat.save()
        else:
            opentok_session_id = chat.opentok_session_id

        token, api_key, session_id = get_opentok_details(opentok_session_id)
        api_key = Opentok.get_api_key()
        session_id = opentok_session_id

        data = {
            "token": token,
            "sessionId": session_id,
            "apiKey": api_key
        }

        other_user = chat.userB if chat.userA == user else chat.userA
        GCMNotificaiton().send_ringing_notification(other_user.fcm_token, user.gender, chat)

        return JsonResponse({"session": data})
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


@api_view(['POST'])
def update_ratings(request):
    try:
        user_uuid, password = utils.retrieve_username_password_from_authorization(request)
        if not Users.objects.filter(user_uuid=user_uuid).exists():
            return error_response("Unauthorized Access", 401)
        user = Users.objects.get(user_uuid=user_uuid)
        data = json.loads(request.body)
        opentok_session_id = data['opentok_session_id']
        ratings = data['ratings']
        chat = Chats.objects.get(opentok_session_id=opentok_session_id)
        if chat.userA == user:
            other_user = chat.userB
            rating_existed = True if chat.rating_by_userA else False
            chat.rating_by_userA = ratings
        else:
            other_user = chat.userA
            rating_existed = True if chat.rating_by_userB else False
            chat.rating_by_userB = ratings
        chat.save()

        if not rating_existed:
            if chat.rating_by_userA and chat.rating_by_userB:  # Notification  # send notificaiton only when both user completed
                GCMNotificaiton().send_ratings_feedback_notification(chat.id)

            total_counts = other_user.avg_rating.get('total_rating_counts', 0)
            for key, val in ratings['rating_params'].items():
                avg_val = other_user.avg_rating.get(key, 0)
                avg_val = ((avg_val * total_counts) + val) / ((total_counts + 1) * 1.0)
                other_user.avg_rating[key] = avg_val
            other_user.avg_rating[TOTAL_RATING_COUNT] = total_counts + 1
            other_user.save()

            return JsonResponse({"status": "ok"})

        else:
            return error_response("You have already rated this User for Same Call", 400)
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


@api_view(['GET'])
def get_filters(request):
    try:
        user_uuid, password = utils.retrieve_username_password_from_authorization(request)
        if not Users.objects.filter(user_uuid=user_uuid).exists():
            return error_response("Unauthorized Access", 401)

        user = Users.objects.get(user_uuid=user_uuid)
        filters = user.filters if user.filters else None

        res_data = {
            "filters": filters
        }
        return JsonResponse(res_data)
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


@api_view(['POST'])
def update_chats(request):
    data = json.loads(request.body)
    username, password = retrieve_username_password_from_authorization(request)
    if username != Opentok.get_api_key():
        return error_response('Unauthorized Access', 401)
    chat_id = data.get('chat_id', None)
    if chat_id:
        Chats.objects.filter(id=chat_id).delete()
        return JsonResponse({"status": "deleted"})

    if data['usera_uuid'] == data['userb_uuid']:
        return error_response("Cannot schedule call between same users")

    userA = Users.objects.get(user_uuid=data['usera_uuid'])
    userB = Users.objects.get(user_uuid=data['userb_uuid'])
    next_seconds = int(data['next_seconds'])
    chat_time = now() + timedelta(0, next_seconds)

    q1 = Q(userA=userA) & Q(userB=userB)
    q2 = Q(userA=userB) & Q(userB=userA)
    from_time = now() - timedelta(1, 0)
    q3 = Q(chat_time__gte=from_time)
    q = Q(Q(q1 | q2) & q3)
    if Chats.objects.filter(q).exists():
        return error_response("You cannot schedule a call, u already have a chat scheduled since past day")
    chat = Chats(userB=userB, userA=userA, chat_time=chat_time)
    chat.save()
    GCMNotificaiton().send_chat_scheduled_notificaiton(chat.id)
    return JsonResponse({"status": "created"})


@api_view(['POST'])
def notification(request):
    try:
        data = json.loads(request.body)
        user_uuid, password = utils.retrieve_username_password_from_authorization(request)
        if not Users.objects.filter(user_uuid=user_uuid).exists():
            return error_response("Unauthorized Access", 401)

        fcm_token = data['fcm_token']
        notification_type = data['notification_type']

        if notification_type == "CALL ENDED NOTIFICATION":
            GCMNotificaiton().send_call_ended_notification(fcm_token)

        return JsonResponse({"status":"ok"})
    except Exception as e:
        logger.exception(e.message)
        return error_response("Server Error", 500)


def get_current_or_next_chat_for_user(user_uuid):
    user = Users.objects.filter(user_uuid=user_uuid).first()
    from_time = utils.now() - timedelta(0, SECONDS)
    chats = Chats.objects.filter(Q(Q(userA=user) | Q(userB=user)), chat_time__gte=from_time)

    if not chats.exists():
        return None, None
    else:
        chat = chats.first()
        now = utils.now()
        if chat.chat_time > now:
            on_going_chat = False
        else:
            on_going_chat = True
        return chat, on_going_chat


def generate_opentok_session():
    optok = Opentok.objects.filter(mode='development').first()
    opentok = OpenTok(optok.api_key, optok.api_secret)
    session = opentok.create_session(media_mode=MediaModes.routed, archive_mode=ArchiveModes.always)
    return session.session_id


def get_opentok_details(opentok_session_id, chat_time=0):
    optok = Opentok.objects.filter(mode='development').first()
    opentok = OpenTok(optok.api_key, optok.api_secret)
    token = opentok.generate_token(opentok_session_id)
    api_key = Opentok.get_api_key()
    session_id = opentok_session_id
    return token, api_key, session_id


def test(request):
    return JsonResponse({"author": "Anas MD"})


def new_chat(request):
    return None


