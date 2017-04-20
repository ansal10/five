from __future__ import unicode_literals

import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
from fiveapp.utils import now


def get_uuid():
    return uuid.uuid4().__str__()


class Users(models.Model):
    user_uuid = models.CharField(default=get_uuid, db_index=True, max_length=63)
    facebook_id = models.CharField(db_index=True, max_length=255, null=True)
    firebase_user_id = models.CharField(db_index=True, max_length=255, null=False)
    last_visited = models.DateTimeField()
    fb_link = models.CharField(max_length=255)
    fb_data = JSONField(default={}, null=True)
    filters = JSONField(default={}, null=True)
    avg_rating = JSONField(default={}, null=True)
    name = models.CharField(null=True, max_length=255)
    email = models.CharField(null=True, max_length=255)
    gender = models.CharField(null=True, max_length=255)
    fb_profile_data = JSONField(default={})
    fcm_token = models.CharField(max_length=255, null=True)
    app_id = models.CharField(max_length=255, null=True)
    timezone = models.CharField(max_length=15, null=True)




    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.last_visited = now()
        super(Users, self).save(*args, **kwargs)

    def to_json(self):
        return self


class Chats(models.Model):
    userA = models.ForeignKey(Users, related_name='userA', db_index=True)
    userB = models.ForeignKey(Users, related_name='userB', db_index=True)
    chat_time = models.DateTimeField(max_length=255, db_index=True)
    opentok_session_id = models.CharField(max_length=255, db_index=True, null=True)
    rating_by_userA = JSONField(default={}, null=True)
    rating_by_userB = JSONField(default={}, null=True)
    chat_notified_times = models.IntegerField(default=0, db_index=True)
    rating_notified_times = models.IntegerField(default=0, db_index=True)

    def to_json(self):
        return self


class Opentok(models.Model):
    mode = models.CharField(max_length=31)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)

    @classmethod
    def get_api_key(cls):
        optok = Opentok.objects.filter(mode='development').first()
        return optok.api_key

