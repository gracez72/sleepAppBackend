from django.db import models 
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import time
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    name = models.CharField(max_length=100, default="name")
    image = models.ImageField(blank=True, upload_to="images/", default='images/moon.jpg')

DEFAULT_USER_ID = 1
class Alarm(models.Model):
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    alarm_time = models.DateTimeField(unique=True)
    youtube_link = models.CharField(max_length=255, default='')
    volume = models.IntegerField(default=5)
    active = models.BooleanField(default=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE, default=DEFAULT_USER_ID)

    class Meta:
        ordering = ('created_on',)

    def __str__(self):
        return str(self.alarm_time)    

class Event(models.Model):
    event_name = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    username = models.ForeignKey(User, on_delete=models.CASCADE,default=DEFAULT_USER_ID)


    class Meta:
        ordering = ('start_time',)

    def __str__(self):
        return str(self.event_name)    


class Song(models.Model):
    youtube_link = models.TextField()
    username = models.ForeignKey(User, on_delete=models.CASCADE, default=DEFAULT_USER_ID)


    class Meta:
        ordering = ('youtube_link',)

    def __str__(self):
        return str(self.youtube_link)   

    
class SleepData(models.Model):
    oxygen_level = models.IntegerField()
    date = models.DateTimeField()
    heart_rate = models.IntegerField()
    username = models.ForeignKey(User, on_delete=models.CASCADE, default=DEFAULT_USER_ID)


    class Meta:
        ordering = ('date',)

    
    def __str__(self):
        return str(self.date)

