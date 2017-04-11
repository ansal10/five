from django.test import TestCase

from fiveapp.models import Users, Chats
from fiveapp.utils import now
from utilities.gcm_notification import GCMNotificaiton


def mocked_send_notificaiton(self, registration_id, message_title, message_body, data_message=None):
    pass

class GCMNotificationTests(TestCase):

    def setUp(self):
        self.usera, _ = Users.objects.get_or_create(fcm_token="token1")
        self.userb, _ = Users.objects.get_or_create(fcm_token="token2")
        self.chat = Chats(userA=self.usera, userB=self.userb, chat_time=now())
        self.chat.save()

    def tearDown(self):
        pass

    def test_send_chat_scheduled_notificaiton(self):
        gcm = GCMNotificaiton()
        gcm.send_chat_scheduled_notificaiton(self.chat.id)
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.notified_times, 1)
