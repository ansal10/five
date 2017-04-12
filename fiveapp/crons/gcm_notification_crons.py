from datetime import timedelta

import logging
from django.db.models import Q

from fiveapp.models import Chats
from fiveapp.utils import now
from utilities.gcm_notification import GCMNotificaiton
logger = logging.getLogger('cron')


def send_notification_before_five_mins_of_scheduled_call(arg):
    chat_ids = eval(arg) if arg else None  # arg = [1,2, 3]
    chat_from = now()
    chat_till = now() + timedelta(0, 300)
    if arg:
        chats = Chats.objects.filter(id__in=chat_ids)
    else:
        chats = Chats.objects.filter(chat_time__gte=chat_from, chat_time__lte=chat_till, chat_notified_times=0)

    for chat in chats:
        logger.info("Sending 5 min Notificaiton for chat id {}".format(chat.id))
        GCMNotificaiton().send_chat_reminder_notification(chat.id)


def send_notification_for_rating_feedbacks(arg):
    chats = Chats.objects.filter(~Q(rating_by_userA=None) & ~Q(rating_by_userB=None) & Q(rating_notified_times=0))
    for chat in chats:
        GCMNotificaiton().send_ratings_feedback_notification(chat.id)
