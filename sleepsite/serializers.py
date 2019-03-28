from rest_framework import serializers
from .models import Alarm, SleepData, Event, Song, Profile
from django.contrib.auth.models import User

class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        fields = ('id', 'description', 'created_on', 'alarm_time', 'youtube_link', 'volume', 'active', 'username')


class SleepDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = SleepData
        fields = ('id', 'oxygen_level', 'date', 'heart_rate', 'username')


class EventSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Event
        fields = ('id', 'event_name', 'start_time', 'end_time', 'username')

class SongSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Song
        fields = ('id', 'youtube_link', 'username')

class ProfileSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Profile
        fields = ('user', 'bio', 'name', 'location', 'image')

class UserSerializer(serializers.ModelSerializer):

    class Meta: 
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name') 
