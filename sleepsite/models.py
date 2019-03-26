from django.db import models 
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import time
import datetime

# Create your models here.

def path_and_rename(instance, filename):
    upload_to = 'event_pics'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

class Alarm(models.Model):
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    alarm_time = models.DateTimeField(unique=True)
    youtube_link = models.CharField(max_length=255, default='')
    volume = models.IntegerField(default=5)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created_on',)

    def __str__(self):
        return str(self.alarm_time)    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    image = models.ImageField(upload_to=path_and_rename, default=None)

class Event(models.Model):
    event_name = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ('start_time',)

    def __str__(self):
        return str(self.event_name)    


class Song(models.Model):
    youtube_link = models.TextField()

    class Meta:
        ordering = ('youtube_link',)

    def __str__(self):
        return str(self.youtube_link)   

    
class SleepData(models.Model):
    oxygen_level = models.IntegerField()
    date = models.DateTimeField()
    heart_rate = models.IntegerField()


    class Meta:
        ordering = ('date',)

    
    def __str__(self):
        return str(self.date)

