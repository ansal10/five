import base64
import json

from datetime import datetime, timedelta
from django.test import Client

from django.test import TestCase
from minimocktest import MockTestCase
import mock
from fiveapp.models import Users, Chats, Opentok
from fiveapp.utils import now


# def simple_generate_token(session_id):
#     return 'token1'

def get_opentok_details(session_id):
    return 'token1', '11', 'session1'

def simple_generate_session():
    return 'session1'


class UserTests(TestCase, MockTestCase):
    def setUp(self):
        self.client = Client()
        Opentok(mode='development', api_key='11', api_secret='2121').save()

    def tearDown(self):
        pass

    def auth_headers(self, username, password):
        credentials = base64.encodestring('%s:%s' % (username, password)).strip()
        auth_string = 'Basic %s' % credentials
        header = {'HTTP_AUTHORIZATION': auth_string}
        return header

    def test_to_check_creation_of_user(self):
        data = {'facebook_id': '11', 'firebase_user_id': '22', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data),
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        assert response.status_code == 200
        assert Users.objects.all().count() == 1

    def test_to_check_creation_of_user_without_firebase_user_id(self):
        data = {'facebook_id': '11', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user',
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        assert response.status_code == 400
        assert Users.objects.all().count() == 0

    def test_to_check_re_post_of_user(self):
        data = {'facebook_id': '11', 'firebase_user_id': '22', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data),
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        response = self.client.post('/fiveapp/user', json.dumps(data),
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        assert response.status_code == 200
        assert Users.objects.all().count() == 1

    def test_chat_time_for_existing_user(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        response = self.client.post('/fiveapp/next_chat',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertIsNone(res_data['chat'])

    @mock.patch('fiveapp.views.get_opentok_details', side_effect=get_opentok_details)
    @mock.patch('fiveapp.views.generate_opentok_session', side_effect=simple_generate_session)
    def test_chat_time_for_user_with_scheduled_chat(self, x, y):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        Chats(userA=user, userB=user, chat_time=now()).save()
        response = self.client.post('/fiveapp/next_chat',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertIn( 'seconds_left_for_chat_start',  res_data['chat'] )
        self.assertIn('token', res_data['chat']['session_data'])

    def test_chat_time_for_user_with_expired_time(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        chat_time = now() - timedelta(0, 300)
        Chats(userA=user, userB=user, chat_time=chat_time).save()
        response = self.client.post('/fiveapp/next_chat',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertIsNone(res_data['chat'])


    def test_chat_time_for_user_with_future_time(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        chat_time = now() + timedelta(0, 600)
        Chats(userA=user, userB=user, chat_time=chat_time).save()
        response = self.client.post('/fiveapp/next_chat',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertIn('seconds_left_for_chat_start', res_data['chat'])
        self.assertNotIn('session_data', res_data['chat'])


    @mock.patch('fiveapp.views.get_opentok_details', side_effect=get_opentok_details)
    def test_opentok_session_id(self, urandom_function):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        Chats(userA=user, userB=user, chat_time=now(), opentok_session_id='1212').save()
        response = self.client.post('/fiveapp/get_session',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertEqual(res_data['session']['sessionId'], '1212')
        self.assertEqual(res_data['session']['token'], 'token1')

    @mock.patch('fiveapp.views.get_opentok_details', side_effect=get_opentok_details)
    @mock.patch('fiveapp.views.generate_opentok_session', side_effect=simple_generate_session)
    def test_generation_of_new_opentok_session_id(self, x1, x2):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        Chats(userA=user, userB=user, chat_time=now()).save()
        response = self.client.post('/fiveapp/get_session',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertEqual(res_data['session']['sessionId'], 'session1')
        self.assertEqual(res_data['session']['token'], 'token1')

    def test_update_user_details(self):
        user = Users()
        user.save()
        data = {"fb_data":{"a":"a"}, "filters":{"b":"b"}}
        response = self.client.post('/fiveapp/update_user_details', json.dumps(data), content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertIn("a", user.fb_data)
        self.assertIn("b", user.filters)

    def test_update_null_user_details(self):
        user = Users(fb_data={"a":"a"})
        user.save()
        data = {"fb_data":None, "filters":{"b":"b"}}
        response = self.client.post('/fiveapp/update_user_details', json.dumps(data), content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertIn("a", user.fb_data)
        self.assertIn("b", user.filters)