import datetime

import pytz
from django.db import transaction
from django.test import TestCase

from fiveapp.models import Users, Chats
from fiveapp.utils import now, check_call_schedule_compatiblity
from utilities.gcm_notification import GCMNotificaiton



class ChatSchedulerTest(TestCase):

    def setUp(self):
        self.usera, _ = Users.objects.get_or_create(fcm_token="token1", fb_link="link1", timezone='Asia/Kolkata')
        self.userb, _ = Users.objects.get_or_create(fcm_token="token2", fb_link="link2", timezone='Asia/Kolkata')

    def tearDown(self):
        Users.objects.all().delete()
        Chats.objects.all().delete()

    def test_successful_call_schedule(self):
        self.usera.filters = {
            "monday":True,
            "minTime":"04:11",
            "maxTime":"24:12",
        }
        self.usera.save()

        self.userb.filters = {
            "monday": True,
            "minTime": "08:11",
            "maxTime": "16:12",
        }
        self.userb.save()
        chat_time = datetime.datetime(2017, 4, 3, 5, tzinfo=pytz.utc )

        x = check_call_schedule_compatiblity(self.usera, self.userb, chat_time)
        self.assertTrue(x)

    def test_un_successful_call_schedule_different_day_same_timezone(self):
        self.usera.filters = {
            "tuesday":True,
            "minTime":"04:11",
            "maxTime":"24:12",
        }
        self.usera.save()

        self.userb.filters = {
            "monday": True,
            "minTime": "08:11",
            "maxTime": "16:12",
        }
        self.userb.save()
        chat_time = datetime.datetime(2017, 4, 3, 5, tzinfo=pytz.utc )

        x = check_call_schedule_compatiblity(self.usera, self.userb, chat_time)
        self.assertFalse(x)

    def test_successful_call_schedule_different_timezone(self):
        with transaction.atomic():
            self.usera.filters = {
                "monday":True,
                "minTime":"04:11",
                "maxTime":"23:12",
            }
            self.usera.timezone = 'America/New_York'
            self.usera.save()

            self.userb.filters = {
                "tuesday": True,
                "minTime": "08:11",
                "maxTime": "16:12",
            }
            self.userb.save()

        chat_time = datetime.datetime(2017, 4, 4, 3, tzinfo=pytz.utc )

        x = check_call_schedule_compatiblity(self.usera, self.userb, chat_time)
        self.assertTrue(x)
