# Generated by Django 2.1.1 on 2019-02-27 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sleepsite', '0010_auto_20190226_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]
