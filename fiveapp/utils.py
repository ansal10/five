import base64
import json
from datetime import datetime
from functools import wraps
import facebook

import pytz
from django.http import JsonResponse

FB_PROFILE_FIELDS = 'id,name,email,gender,first_name,last_name,link,relationship_status,cover'

def now():
    return datetime.now(pytz.utc)


def retrieve_username_password_from_authorization(request):
    auth_header = request.META['HTTP_AUTHORIZATION']
    encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    username = decoded_credentials[0]
    password = decoded_credentials[1]

    return username, password



def update_user_fb_profile_data(user):
    token = user.fb_data['token']
    graph = facebook.GraphAPI(access_token=token)
    d = graph.get_object('me', fields=FB_PROFILE_FIELDS)
    user.fb_profile_data = d
    user.name = d['name']
    user.email = d['email']
    user.gender = d['gender']
    user.fb_link = d['link']
    user.save()
    return user


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.__str__()
        else:
            encoded_object =super(DateTimeEncoder, self).default(obj)
        return encoded_object