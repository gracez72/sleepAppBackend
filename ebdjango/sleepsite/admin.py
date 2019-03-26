from django.contrib import admin
from .models import Alarm, SleepData, Event, Song

# Register your models here.
admin.site.register(Alarm)
admin.site.register(SleepData)
admin.site.register(Event)
admin.site.register(Song)

