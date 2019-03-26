from rest_framework import serializers
from .models import Alarm, SleepData, Event, Song

class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        fields = ('id', 'description', 'created_on', 'alarm_time', 'youtube_link', 'volume', 'active')


class SleepDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = SleepData
        fields = ('id', 'oxygen_level', 'date', 'heart_rate')


class EventSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Event
        fields = ('id', 'event_name', 'start_time', 'end_time')

class SongSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Song
        fields = ('id', 'youtube_link')