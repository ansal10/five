import logging
from datetime import timedelta

from django.db.models import Q

from pyfcm import FCMNotification

from config import FIREBASE_API_KEY, SECONDS
from fiveapp.models import Users, Chats
from fiveapp.utils import now

logger = logging.getLogger('fiveapp')
NOTIFICATION_TYPE = "notification_type"
FEEDBACK_NOTIFICATION = "FEEDBACK NOTIFICATION"
CALL_ENDED_NOTIFICATION = "CALL ENDED NOTIFICATION"
RINGING_NOTIFICATION = "RINGING NOTIFICATION"
GENDER_KEY = "gender"


class GCMNotificaiton(object):
    def __init__(self):
        self.push_service = FCMNotification(api_key=FIREBASE_API_KEY)

    def send_notificaiton(self, registration_id, message_title, message_body, data_message=None):
        logger.info("Sending notification to reg_id={}, title={}, body={}, data={}"
                    .format(registration_id, message_title, message_body, data_message))
        result = self.push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                        message_body=message_body, sound='default',
                                                        data_message=data_message)
        logger.info("Result={}".format(result))

    def send_data_only_notification(self, registration_id, message_title, message_body, data_message=None):
        logger.info("Sending data only notification to reg_id={}, title={}, body={}, data={}"
                    .format(registration_id, message_title, message_body, data_message))
        result = self.push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                        message_body=message_body, sound='default',
                                                        data_message=data_message, data_only=True)
        logger.info("Result={}".format(result))

    def send_chat_scheduled_notificaiton(self, chat_id):
        chat = Chats.objects.get(id=chat_id)
        users = [chat.userA, chat.userB]

        for user in users:
            title = "Your Call has been scheduled"
            next_time_diff = "{} hour and {} minutes".format((chat.chat_time - now()).days * 24,
                                                             (chat.chat_time - now()).seconds / 60)
            message = "Hi {}, Congratulations! We have scheduled a call in next {}". \
                format(user.name, next_time_diff)
            data_message = {}
            self.send_notificaiton(user.fcm_token, title, message, data_message)

        chat.chat_notified_times += 1
        chat.save()

    def send_chat_reminder_notification(self, chat_id):
        chat = Chats.objects.get(id=chat_id)
        users = [chat.userA, chat.userB]
        for user in users:
            title = "Reminder for Your Scheduled Call in next few minutes"
            next_time_diff = "{} seconds".format((chat.chat_time - now()).seconds)
            message = "Hi {}, Just a reminder that your next call is scheduled in {}". \
                format(user.name, next_time_diff)
            data_message = {}
            self.send_notificaiton(user.fcm_token, title, message, data_message)

        chat.chat_notified_times += 1
        chat.save()

    def send_ratings_feedback_notification(self, chat_id):
        chat = Chats.objects.get(id=chat_id)
        users = [chat.userA, chat.userB]

        for user in users:
            other_user_ratings = chat.rating_by_userA if chat.userB == user else chat.rating_by_userB
            data_message = {
                NOTIFICATION_TYPE: FEEDBACK_NOTIFICATION,
                "has_shared_profile": other_user_ratings['share_profile'],
                "message": other_user_ratings['share_message'],
                "facebook_link": users[0].fb_link if users[1] == user else users[1].fb_link
            }
            title = "Feedback for your recent chat"
            message = "Hi {}, You have received a feedback for your recent chat scheduled on {}". \
                format(user.name, chat.chat_time.strftime("%d, %b %Y"))
            self.send_notificaiton(user.fcm_token, title, message, data_message=data_message)

        chat.rating_notified_times += 1
        chat.save()

    def send_call_ended_notification(self, fcm_token):
        data_message = {
            NOTIFICATION_TYPE: CALL_ENDED_NOTIFICATION,
        }
        title="Your call has ended"
        message = ""
        self.send_notificaiton(fcm_token, title, message, data_message)

    def send_ringing_notification(self, fcm_token, gender, chat):
        data_message = {
            NOTIFICATION_TYPE: RINGING_NOTIFICATION,
            GENDER_KEY: gender,
            "chat_start_time": chat.chat_time.__str__(),
            "chat_end_time": (chat.chat_time + timedelta(0, SECONDS)).__str__(),
            "current_time": now().isoformat().__str__(),
            "gender": gender,
            "fcm_token": fcm_token
        }
        self.send_data_only_notification(fcm_token, "", "", data_message=data_message )
