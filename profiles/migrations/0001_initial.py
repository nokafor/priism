# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conflict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(verbose_name=b'Start Time')),
                ('end_time', models.TimeField(verbose_name=b'End Time')),
                ('day_of_week', models.CharField(default=b'Mon', max_length=3, choices=[(b'Mon', b'Monday'), (b'Tue', b'Tuesday'), (b'Wed', b'Wednesday'), (b'Thu', b'Thursday'), (b'Fri', b'Friday'), (b'Sat', b'Saturday'), (b'Sun', b'Sunday')])),
                ('description', models.CharField(max_length=200)),
                ('member', models.ForeignKey(to='companies.Member')),
            ],
            options={
                'ordering': ['day_of_week', 'start_time'],
            },
        ),
    ]
