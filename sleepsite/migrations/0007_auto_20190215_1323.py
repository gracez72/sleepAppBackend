# Generated by Django 2.1.1 on 2019-02-15 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sleepsite', '0006_auto_20190215_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alarm',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='sleepdata',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
