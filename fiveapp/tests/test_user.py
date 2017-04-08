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

def mock_update_user_fb_profile_data(user):
    return user

def auth_headers( username, password=''):
    credentials = base64.encodestring('%s:%s' % (username, password)).strip()
    auth_string = 'Basic %s' % credentials
    header = {'HTTP_AUTHORIZATION': auth_string}
    return header

class UserTests(TestCase):
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

    @mock.patch('fiveapp.apis.update_user_fb_profile_data', side_effect=mock_update_user_fb_profile_data)
    def test_to_check_creation_of_user(self, x):
        data = {'facebook_id': '11', 'firebase_user_id': '22', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data),
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        assert response.status_code == 200
        assert Users.objects.all().count() == 1
        res = json.loads(response.content)
        self.assertIn('filters' , res)

    @mock.patch('fiveapp.apis.update_user_fb_profile_data', side_effect=mock_update_user_fb_profile_data)
    def test_to_check_creation_of_user_without_firebase_user_id(self, x):
        data = {'facebook_id': '11', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user',
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        assert response.status_code == 400
        assert Users.objects.all().count() == 0

    @mock.patch('fiveapp.apis.update_user_fb_profile_data', side_effect=mock_update_user_fb_profile_data)
    def test_to_check_re_post_of_user(self, x):
        data = {'facebook_id': '11', 'firebase_user_id': '22', 'fb_data': {'name': 'xyz', 'age': '22'}}
        response = self.client.post('/fiveapp/user', json.dumps(data),
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        user = Users.objects.first()
        user.filters = {'age':22}
        user.save()
        response = self.client.post('/fiveapp/user', json.dumps(data),
                                    content_type="application/json", **self.auth_headers('XX', 'YY'))
        res = json.loads(response.content)
        assert response.status_code == 200
        assert Users.objects.all().count() == 1
        self.assertIn('age', res['filters'])

    def test_chat_time_for_existing_user(self):
        user = Users()
        user.save()
        data = {"user_uuid": user.user_uuid}
        response = self.client.post('/fiveapp/next_chat',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertIsNone(res_data['chat'])

    @mock.patch('fiveapp.apis.get_opentok_details', side_effect=get_opentok_details)
    @mock.patch('fiveapp.apis.generate_opentok_session', side_effect=simple_generate_session)
    def test_chat_time_for_user_with_scheduled_chat(self, x, y):
        user = Users(gender='male')
        other_user = Users(gender='female')
        other_user.save()
        user.save()
        data = {"user_uuid": user.user_uuid}
        Chats(userA=user, userB=other_user, chat_time=now()).save()
        response = self.client.post('/fiveapp/next_chat',
                                    content_type="application/json", **self.auth_headers(user.user_uuid, ''))
        assert response.status_code == 200
        res_data = json.loads(response.content)
        self.assertEqual(res_data['chat']['user']['gender'], 'female')
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


    @mock.patch('fiveapp.apis.get_opentok_details', side_effect=get_opentok_details)
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

    @mock.patch('fiveapp.apis.get_opentok_details', side_effect=get_opentok_details)
    @mock.patch('fiveapp.apis.generate_opentok_session', side_effect=simple_generate_session)
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

    def test_retrive_null_filters(self):
        user = Users()
        user.save()
        response = self.client.get('/fiveapp/get_filters', **self.auth_headers(user.user_uuid, ''))
        self.assertEqual(response.status_code, 200)
        res =  json.loads(response.content)
        self.assertIsNone(res['filters'])

    def test_retrive_existing_filters(self):
        user = Users(filters={'age_min':22, 'age_max':25, 'looking_for':['male', 'female']})
        user.save()
        response = self.client.get('/fiveapp/get_filters', **self.auth_headers(user.user_uuid, ''))
        self.assertEqual(response.status_code, 200)
        res =  json.loads(response.content)
        self.assertIn('age_min', res['filters'])
        self.assertIn('male', res['filters']['looking_for'])


class RatingTests(TestCase):

    def setUp(self):
        self.userA, _ = Users.objects.get_or_create(firebase_user_id='12')
        self.userB, _ = Users.objects.get_or_create(firebase_user_id='21')
        self.chat, _ = Chats.objects.get_or_create(userA=self.userA, userB=self.userB, chat_time = now(), opentok_session_id='111')
        self.client = Client()
        pass

    def tearDown(self):
        Users.objects.all().delete()
        Chats.objects.all().delete()
        pass

    def test_rating_first_time(self):
        data = {'opentok_session_id':'111', 'ratings':{'rating_params':{'looks':5, 'feels':3}, 'feedback':'this is new', 'share_profile':True}}
        res = self.client.post('/fiveapp/ratings', json.dumps(data), content_type='application/json', **auth_headers(self.userA.user_uuid))
        self.assertEqual(res.status_code, 200)
        self.userB.refresh_from_db()
        self.assertIn('total_rating_counts', self.userB.avg_rating)
        self.assertEqual(self.userB.avg_rating['total_rating_counts'], 1)
        self.assertEqual(self.userB.avg_rating['looks'], 5)


    def test_rating_second_time(self):
        self.chat.rating_by_userA = {'looks':1, 'total_rating_counts':2}
        self.chat.save()
        data = {'opentok_session_id':'111', 'ratings':{'rating_params':{'looks':5, 'feels':3}, 'feedback':'this is new', 'share_profile':True}}
        res = self.client.post('/fiveapp/ratings', json.dumps(data), content_type='application/json',
                               **auth_headers(self.userA.user_uuid))
        self.assertEqual(res.status_code, 400)
        d = json.loads(res.content)
        self.assertIn('error', d)

    def test_both_way_rating(self):
        data = {'opentok_session_id':'111', 'ratings':{'rating_params':{'looks':5, 'feels':3}, 'feedback':'this is new', 'share_profile':True}}
        res = self.client.post('/fiveapp/ratings', json.dumps(data), content_type='application/json',
                               **auth_headers(self.userA.user_uuid))
        res = self.client.post('/fiveapp/ratings', json.dumps(data), content_type='application/json',
                               **auth_headers(self.userB.user_uuid))

        self.assertEqual(res.status_code, 200)
        self.userB.refresh_from_db()
        self.userA.refresh_from_db()
        self.assertIn('total_rating_counts', self.userB.avg_rating)
        self.assertIn('total_rating_counts', self.userA.avg_rating)
        self.assertEqual(self.userB.avg_rating['total_rating_counts'], 1)
        self.assertEqual(self.userA.avg_rating['total_rating_counts'], 1)
        self.assertEqual(self.userB.avg_rating['looks'], 5)
        self.assertEqual(self.userA.avg_rating['looks'], 5)



