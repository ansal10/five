import logging

from django.db.models import Q
from pyfcm import FCMNotification

from config import FIREBASE_API_KEY
from fiveapp.models import Users, Chats
from fiveapp.utils import now

logger = logging.getLogger('fiveapp')


class GCMNotificaiton(object):
    def __init__(self):
        self.push_service = FCMNotification(api_key=FIREBASE_API_KEY)

    def send_notificaiton(self, registration_id, message_title, message_body, data_message=None):
        logger.info("Sending notification to reg_id={}, title={}, body={}, data={}"
                    .format(registration_id, message_title, message_body, data_message))
        result = self.push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                        message_body=message_body, data_message=data_message)
        logger.info("Result={}".format(result))

    def send_chat_scheduled_notificaiton(self, chat_id):
        chat = Chats.objects.get(id=chat_id)
        users = [chat.userA, chat.userB]

        for user in users:
            title = "Call has scheduled"
            next_time_diff = "{} hour and {} minutes".format((chat.chat_time - now()).days * 24,
                                                             (chat.chat_time - now()).seconds / 60)
            message = "Hi {},\nCongratulations! We have scheduled a call in next {}". \
                format(user.name, next_time_diff)
            data_message = {}
            self.send_notificaiton(user.fcm_token, title, message, data_message)

        chat.notified_times += 1
        chat.save()