# Generated by Django 2.1.1 on 2019-02-27 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sleepsite', '0009_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
