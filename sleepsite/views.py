from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Alarm, SleepData, Event, Song, Profile
from .serializers import AlarmSerializer, SleepDataSerializer, EventSerializer, SongSerializer, ProfileSerializer, UserSerializer
from django.db.models import Count, Min, Max, Avg, Sum
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
from django.contrib.auth.models import User

import datetime
from numpy import polyfit 

from rest_framework.decorators import api_view, renderer_classes 
from rest_framework.response import Response 
from rest_framework import permissions

import json
from django.core.serializers.json import DjangoJSONEncoder

from sleepsite import computation

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,) 

class AlarmViewSet(viewsets.ModelViewSet):
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer
    permission_classes = (permissions.AllowAny,) 

    @action(detail=True)
    def js_time(self, request, pk=None):
        """
        Returns datetimefield as js accepted time
        """
        alarm = self.get_object()
        date = alarm.alarm_time.strftime("%Y-%m-%d %H:%M:%S")
        return Response({"time": date})

    def get_queryset(self):
        """
        Allows queryset to be filtered by alarms for given date
        """
        queryset = Alarm.objects.all()
        query_date = self.request.query_params.get('date', None)
        query_user = self.request.query_params.get('username', None)

        if query_date is not None: 
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            queryset = queryset.filter(alarm_time__year=date.year,
                                       alarm_time__month=date.month, 
                                       alarm_time__day=date.day)
            return queryset        
        elif query_user is not None:
            queryset = queryset.filter(username__username=query_user)
        return queryset   

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.AllowAny,) 

    def get_queryset(self):
        queryset = Event.objects.all()
        query_date = self.request.query_params.get('start_time', None)
        
        if query_date is not None: 
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            queryset = queryset.filter(start_time__year=date.year,
                                        start_time__month=date.month, 
                                        start_time__day=date.day)
            for obj in queryset:
                obj.date = obj.date.strftime("%Y-%m-%d %H:%M:%S")

        return queryset

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes =(permissions.AllowAny,) 

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.AllowAny,) 


class SleepDataViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,) 
    queryset = SleepData.objects.all()
    serializer_class = SleepDataSerializer

    def get_queryset(self):
        """
        Allows sleepdata to be filtered by given date or date range
        """
        queryset = SleepData.objects.all()
        query_date = self.request.query_params.get('date', None)
        query_start_date = self.request.query_params.get('start_date', None)
        query_end_date = self.request.query_params.get('end_date', None)
        
        if query_date is not None: 
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            queryset = queryset.filter(date__year=date.year,
                                       date__month=date.month, 
                                       date__day=date.day)
            for obj in queryset:
                obj.date = obj.date.strftime("%Y-%m-%d %H:%M:%S")

            return queryset

        if None not in (query_start_date, query_end_date):
            start_date = datetime.datetime.strptime(query_start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(query_end_date, '%Y-%m-%d').date()

            if start_date.year == end_date.year:
                queryset = queryset.filter(date__range=[start_date, end_date])

            for obj in queryset:
                obj.date = obj.date.strftime("%Y-%m-%d %H:%M:%S")          

            return queryset
        
        return queryset  

class ComputationViewSet(viewsets.ViewSet):
    """
    A view that returns computation results eg. approximate function, peaks, etc.
    """

    def list(self, request, format=None):
        """
        Given date or date range, returns: 
            number of local maxima given data
            id of peak sleepdata objects
            list of sleepdata peak times
            degree of polynomial fit for data
            list of coefficients of polynomial fit function
            bin data for heartrate and oxygen level
        """
        queryset = SleepData.objects.all()

        query_date = self.request.query_params.get('date', None)            
        query_start_date = self.request.query_params.get('start_date', None)
        query_end_date = self.request.query_params.get('end_date', None)

        if query_date is not None: 
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            queryset = queryset.filter(date__year=date.year,
                                       date__month=date.month, 
                                       date__day=date.day)

            data = list(queryset.values_list('heart_rate', flat=True))
            ol_data = list(queryset.values_list('oxygen_level', flat=True))

            if len(data) > 0: 

                # Heart rate binning: 
                hr_bins_list, ol_bins_list, hr_bin_count, ol_bin_count = computation.getBins(queryset)
                id_index, peaks, num_peaks, sleepdata_index, sleepdata_peaks, degree, coefficients = computation.getPeaks(queryset)
                
                ol_bin, hr_bin = computation.getFormattedBins(hr_bins_list, ol_bins_list, hr_bin_count, ol_bin_count)
                results = computation.getFunctionPoints(coefficients, degree, len(data))

                if None not in (data):
                    return JsonResponse({
                        "id_index": id_index,
                        "peaks": peaks,
                        "num_peaks": num_peaks,
                        "sleepdata_id_index": sleepdata_index,
                        "sleepdata_time": sleepdata_peaks,
                        "degree": degree,
                        "coefficients" : coefficients,
                        "hr_bin_list": hr_bins_list,
                        "ol_bin_list": ol_bins_list,
                        "hr_bin_count": hr_bin_count,
                        "ol_bin_count": ol_bin_count,
                        "ol_bins": ol_bin,
                        "hr_bins": hr_bin,
                        "function": results,
                    })
            else: 
                return JsonResponse({
                    "error": "no data available for given date"
                })

        elif None not in (query_start_date, query_end_date):            
            
            start_date = datetime.datetime.strptime(query_start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(query_end_date, '%Y-%m-%d').date()

            if start_date.year == end_date.year:
                queryset = queryset.filter(date__range=[start_date, end_date])

            
            data = list(queryset.values_list('heart_rate', flat=True))
            ol_data = list(queryset.values_list('oxygen_level', flat=True))


            if len(data) > 0 and len(ol_data) > 0:         
                hr_bins_list, ol_bins_list, hr_bin_count, ol_bin_count = computation.getBins(queryset)
                id_index, peaks, num_peaks, sleepdata_index, sleepdata_peaks, degree, coefficients = computation.getPeaks(queryset)

                ol_bin, hr_bin = computation.getFormattedBins(hr_bins_list, ol_bins_list, hr_bin_count, ol_bin_count)
                results = computation.getFunctionPoints(coefficients, degree, len(data))

                return JsonResponse({
                    "id_index": id_index,
                    "peaks": peaks,
                    "num_peaks": num_peaks,
                    "sleepdata_id_index": sleepdata_index,
                    "sleepdata_time": sleepdata_peaks,
                    "degree": degree,
                    "coefficients" : coefficients,
                    "hr_bin_list": hr_bins_list,
                    "ol_bin_list": ol_bins_list,
                    "hr_bin_count": hr_bin_count,
                    "ol_bin_count": ol_bin_count,
                    "ol_bins": ol_bin,
                    "hr_bins": hr_bin,
                    "function": results,
                })
            else: 
                return JsonResponse({
                    "error": "date range accepted but no data found"
                })

        else:
            return JsonResponse({
                "error": 'no data found'
            })

        return JsonResponse({
                    "error": 'no date range given'
                })

class SongSummaryViewSet(viewsets.ViewSet):
    """
    A view that returns song summary stats
    """
    def list(self, request, format=None):
        queryset = Song.objects.all()
        song_count = queryset.aggregate(Count('id'))['id__count']

        return JsonResponse({
            "song_count": song_count
        })

class SummaryViewSet(viewsets.ViewSet):

    """
    A view that returns filtered summary stats for all data
    """
    def list(self, request, format=None):
        """
        Returns aggregate data for given date or date range
        """
        queryset = SleepData.objects.all()

        query_date = self.request.query_params.get('date', None)
        query_start_date = self.request.query_params.get('start_date', None)
        query_end_date = self.request.query_params.get('end_date', None)
        
        if query_date is not None: 
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            queryset = queryset.filter(date__year=date.year,
                                       date__month=date.month, 
                                       date__day=date.day)
            for obj in queryset:
                obj.date = obj.date.strftime("%Y-%m-%d %H:%M:%S")

            average_hr, max_hr, min_hr, average_ol, max_ol, min_ol = computation.getSummary(queryset)

            max_date, min_date, total_time, total_count, awake_percentage, below_threshold, above_threshold, between_threshold = computation.getStats(queryset)

            if None not in (max_date, min_date, total_time, total_count, awake_percentage, below_threshold, above_threshold, between_threshold):
                return JsonResponse({
                    "average_hr": average_hr,
                    "average_ol": average_ol,
                    "max_hr": max_hr,
                    "max_ol": max_ol,
                    "min_hr": min_hr,
                    "min_ol": min_ol,
                    "total_time": total_time,
                    "max_date": max_date,
                    "min_date": min_date,
                    "total_count": total_count,
                    "awake_percentage": awake_percentage,
                    "below_threshold": below_threshold,
                    "above_threshold": above_threshold,
                    "between_threshold": between_threshold
                })
            else:
                return JsonResponse({
                "error": "No entries match filters"
                })

        if None not in (query_start_date, query_end_date):
            start_date = datetime.datetime.strptime(query_start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(query_end_date, '%Y-%m-%d').date()

            if start_date.year == end_date.year:
                queryset = queryset.filter(date__range=[start_date, end_date])

            for obj in queryset:
                obj.date = obj.date.strftime("%Y-%m-%d %H:%M:%S")          

            average_hr, max_hr, min_hr, average_ol, max_ol, min_ol = computation.getSummary(queryset)
            max_date, min_date, total_time, total_count, awake_percentage, below_threshold, above_threshold, between_threshold = computation.getStats(queryset)

            if None not in (max_date, min_date, total_time, total_count, awake_percentage, below_threshold, above_threshold, between_threshold):
                return JsonResponse({
                    "average_hr": average_hr,
                    "average_ol": average_ol,
                    "max_hr": max_hr,
                    "max_ol": max_ol,
                    "min_hr": min_hr,
                    "min_ol": min_ol,
                    "total_time": total_time,
                    "max_date": max_date,
                    "min_date": min_date,
                    "total_count": total_count,
                    "awake_percentage": awake_percentage,
                    "below_threshold": below_threshold,
                    "above_threshold": above_threshold,
                    "between_threshold": between_threshold
                })
            else:
                return JsonResponse({
                "error": "No entries match filters"
                })

        return JsonResponse({
            "data": list(queryset.values())
        })


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def summary_view(request, format=None):
    """
    A view that returns summary stats in JSON FOR ALL OBJECTS.
    """

    queryset = SleepData.objects.all()

    average_hr, max_hr, min_hr, average_ol, max_ol, min_ol = computation.getSummary(queryset)
    content = {
        'average_hr': average_hr, 
        'average_ol': average_ol,
        'max_hr': max_hr,
        'min_hr': min_hr,
        'average_ol': average_ol,
        'max_ol': max_ol,
        'min_ol': min_ol
    }
    return Response(content)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'alarms': reverse('alarm-list', request=request, format=format), 
        'sleepdata': reverse('sleepdata-list', request=request, format=format),
        'events': reverse('event-list', request=request, format=format),
        'songs': reverse('song-list', request=request, format=format)
    })

