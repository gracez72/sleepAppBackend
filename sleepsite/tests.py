from django.test import TestCase
from sleepsite.models import SleepData
import datetime

class SleepDataTestCase(TestCase):
    def setUp(self):
        SleepData.objects.create(oxygen_level=98, date=datetime.date.today(), heart_rate=67)
        SleepData.objects.create(oxygen_level=97, date=datetime.date.today(), heart_rate=78)

    def sleepdata_date(self):
        """SleepData with specific date are identified"""

        sd1 = SleepData.objects.get(id=1)
        sd2 = SleepData.objects.get(id=2)