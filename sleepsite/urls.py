from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from sleepsite import views
from django.conf.urls import url

router = DefaultRouter()
router.register(r'alarms', views.AlarmViewSet)
router.register(r'sleepdata', views.SleepDataViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'songs', views.SongViewSet)
router.register(r'query-summary', views.SummaryViewSet, base_name='summary')
router.register(r'compute', views.ComputationViewSet, base_name='compute')
router.register(r"song-summary", views.SongSummaryViewSet, base_name='song-summary')

urlpatterns = [
    path('', include(router.urls)),
    path('', views.api_root),
    path('summary/', views.summary_view)
]