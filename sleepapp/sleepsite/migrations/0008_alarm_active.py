# Generated by Django 2.1.1 on 2019-02-17 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sleepsite', '0007_auto_20190215_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
