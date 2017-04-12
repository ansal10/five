from django.test import TestCase

from fiveapp.models import Users, Chats
from fiveapp.utils import now
from utilities.gcm_notification import GCMNotificaiton


def mocked_send_notificaiton(self, registration_id, message_title, message_body, data_message=None):
    pass

class GCMNotificationTests(TestCase):

    def setUp(self):
        self.usera, _ = Users.objects.get_or_create(fcm_token="token1", fb_link="link1")
        self.userb, _ = Users.objects.get_or_create(fcm_token="token2", fb_link="link2")
        self.chat = Chats(userA=self.usera, userB=self.userb, chat_time=now())
        self.chat.save()

    def tearDown(self):
        Users.objects.all().delete()
        Chats.objects.all().delete()

    def test_send_chat_scheduled_notification(self):
        gcm = GCMNotificaiton()
        gcm.send_chat_scheduled_notificaiton(self.chat.id)
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.chat_notified_times, 1)

    def test_send_notification_for_rating_feedbacks(self):
        gcm = GCMNotificaiton()
        self.chat.rating_by_userA = {
            "share_profile":True,
            "share_message":"This text"
        }
        self.chat.rating_by_userB = {
            "share_profile": True,
            "share_message": "This text"
        }
        self.chat.save()
        gcm.send_ratings_feedback_notification(self.chat.id)
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.rating_notified_times, 1)
