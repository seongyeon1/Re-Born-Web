# Generated by Django 3.0.2 on 2020-02-26 09:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('calender', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calender',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 26, 14, 34, 16, 730126, tzinfo=utc), verbose_name='수정일'),
        ),
    ]
