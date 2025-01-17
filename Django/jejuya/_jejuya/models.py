from django.db import models
import os
from uuid import uuid4
import random
import string
from datetime import datetime
from . import utilities as ut



##########
# models.py
# def upload_to(instance, filename): # upload path
# tables
# class UPLOAD(models.Model): # file upload
# class ACCESS_IP(models.Model): # access ip
# class ACCOUNT(models.Model): # 계정 테이블
# class SCHEDULE(models.Model): # 일정 테이블
# class SCHEDULE_ITEM(models.Model): # 일정 아이템 테이블(선택된 관광지)
# class POINT(models.Model): # point(기준점)
# class AROUND(models.Model): # around(관광지)



##########
# models
def upload_to(instance, filename): # upload path
    _, ext = os.path.splitext(filename)
    now = datetime.now()
    formatted_time = now.strftime('%Y%m%d%H%M%S%f')
    new_filename = f'{formatted_time}{ext}'
    return os.path.join('_jejuya/', new_filename)



##########
# tables
class UPLOAD(models.Model): # file upload
    file = models.FileField(upload_to=upload_to)

class ACCESS_IP(models.Model): # access ip
    ip = models.CharField(primary_key=True, max_length=20)
    count = models.DecimalField(max_digits=2, decimal_places=0, help_text="accessible count")
    def save(self, *args, **kwargs):
        if not self.count:
            self.count = 10
        super().save(*args, **kwargs)

class ACCOUNT(models.Model): # 계정 테이블
    id = models.CharField(primary_key=True, max_length=64)
    password = models.CharField(max_length=300)
    device_token = models.CharField(max_length=300, null=True, blank=True)
    account_type = models.CharField(max_length=30) # 'user', 'supervisor'
    dt = models.CharField(max_length=16) # last login datetime
    def save(self, *args, **kwargs):
        self.dt = ut.get_now_dt()
        super().save(*args, **kwargs)

class SCHEDULE(models.Model): # 일정 테이블
    id = models.CharField(primary_key=True, max_length=16)
    user_id = models.CharField(max_length=64)
    date = models.CharField(max_length=10) # YYYY-MM-DD
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ut.get_rand_id(16)
        super().save(*args, **kwargs)
    class MetaData:
        api_permission = {
            "id": "RW",
            "user_id": "RW",
            "date": "RW"
        }

class SCHEDULE_ITEM(models.Model): # 일정 아이템 테이블(선택된 관광지)
    id = models.CharField(primary_key=True, max_length=16)
    schedule_id = models.CharField(max_length=16)
    around_id = models.CharField(max_length=16)
    order = models.IntegerField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ut.get_rand_id(16)
        if not self.order or self.order == 0:
            self.order = SCHEDULE_ITEM.objects.filter(schedule_id=self.schedule_id).count() + 1
        super().save(*args, **kwargs)
    class MetaData:
        api_permission = {
            "id": "RW",
            "schedule_id": "RW",
            "around_id": "RW",
            "order": "RW"
        }

class POINT(models.Model): # point(기준점)
    id = models.CharField(primary_key=True, max_length=16)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    rooms_cnt = models.IntegerField()
    tel = models.CharField(max_length=20)
    note = models.TextField()
    medias = models.TextField() # , separated
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ut.get_rand_id(16)
        if (not self.latitude or self.latitude == '0') or (not self.longitude or self.longitude == '0'):
            lat, lng = ut.generate_random_jeju_coordinates()
            self.latitude = lat
            self.longitude = lng
        if not self.medias or self.medias == '0':
            self.medias = ''
        if not self.rooms_cnt or self.rooms_cnt == 0:
            self.rooms_cnt = 1
        super().save(*args, **kwargs)
    class MetaData:
        api_permission = {
            "id": "RW",
            "name": "RW",
            "address": "RW",
            "latitude": "RW",
            "longitude": "RW",
            "rooms_cnt": "RW",
            "tel": "RW",
            "note": "RW",
            "medias": "RW"
        }

class AROUND(models.Model): # around(관광지)
    id = models.CharField(primary_key=True, max_length=16)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    tel = models.CharField(max_length=20)
    around_type = models.CharField(max_length=30) # 'museum', 'park', 'entertainment', 'sports'..
    categories = models.CharField(max_length=300) # , separated
    open_time = models.CharField(max_length=100)
    holiday = models.CharField(max_length=100)
    reserve_link = models.CharField(max_length=300)
    note = models.TextField()
    medias = models.TextField() # , separated
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ut.get_rand_id(16)
        if (not self.latitude or self.latitude == '0') or (not self.longitude or self.longitude == '0'):
            lat, lng = ut.generate_random_jeju_coordinates()
            self.latitude = lat
            self.longitude = lng
        if not self.open_time or self.open_time == '0':
            self.open_time = '24시간 운영'
        if not self.holiday or self.holiday == '0':
            self.holiday = '없음'
        super().save(*args, **kwargs)
    class MetaData:
        api_permission = {
            "id": "RW",
            "name": "RW",
            "address": "RW",
            "latitude": "RW",
            "longitude": "RW",
            "tel": "RW",
            "around_type": "RW",
            "categories": "RW",
            "open_time": "RW",
            "holiday": "RW",
            "reserve_link": "RW",
            "note": "RW",
            "medias": "RW"
        }


