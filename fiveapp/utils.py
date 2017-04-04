import base64
from datetime import datetime

import pytz


def now():
    return datetime.now(pytz.utc)


def retrieve_username_password_from_authorization(request):
    auth_header = request.META['HTTP_AUTHORIZATION']
    encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    username = decoded_credentials[0]
    password = decoded_credentials[1]

    return username, password
