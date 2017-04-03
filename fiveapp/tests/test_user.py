import json

from datetime import datetime, timedelta
from django.test import Client

from django.test import TestCase

from fiveapp.models import Users, Chats, Opentok
from fiveapp.utils import now


class UserTests(TestCase):
    def setUp(self):
        self.client = Client()
        Opentok(mode='development', api_key='11', api_secret='2121').save()


    def tearDown(self):
        pass

    def test_to_check_creation_of_user(self):
        data = {'facebook_id': '11', 'firebase_id': '22', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data), content_type="application/json")
        assert response.status_code == 200
        assert Users.objects.all().count() == 1


    def test_to_check_creation_of_user_without_firebase_id(self):
        data = {'facebook_id': '11', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data), content_type="application/json")
        assert response.status_code == 400
        assert Users.objects.all().count() == 0

    def test_to_check_re_post_of_user(self):
        data = {'facebook_id': '11', 'firebase_id': '22', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data), content_type="application/json")
        response = self.client.post('/fiveapp/user', json.dumps(data), content_type="application/json")
        assert response.status_code == 200
        assert Users.objects.all().count() == 1

    def test_chat_time_for_existing_user(self):
        user = Users()
        user.save()
        data = {"user_uuid":user.user_uuid}
        response = self.client.post('/fiveapp/get_chat_details', json.dumps(data), content_type="application/json")
        assert response.status_code == 400
        res_data = json.loads(response.content)
        assert res_data['error'] == "You don't have any chats Scheduled"

    def test_chat_time_for_user_with_scheduled_chat(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        Chats(userA=user, userB=user, chat_time=now()).save()
        response = self.client.post('/fiveapp/get_chat_details', json.dumps(data), content_type="application/json")
        assert response.status_code == 200
        res_data = json.loads(response.content)
        assert res_data['chat_time'] is not None

    def test_chat_time_for_user_with_expired_time(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        chat_time = now() - timedelta(0, 300)
        Chats(userA=user, userB=user, chat_time=chat_time).save()
        response = self.client.post('/fiveapp/get_chat_details', json.dumps(data), content_type="application/json")
        assert response.status_code == 400
        res_data = json.loads(response.content)
        assert res_data['error'] == "You don't have any chats Scheduled"


    def test_opentok_session_id(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        Chats(userA=user, userB=user, chat_time=now(), opentok_session_id='1212').save()
        response = self.client.post('/fiveapp/get_session', json.dumps(data), content_type="application/json")
        assert response.status_code == 200
        res_data = json.loads(response.content)
        assert "opentok_session_id" in res_data


