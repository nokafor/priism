# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalRehearsals',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ['member'],
            },
        ),
        migrations.CreateModel(
            name='Cast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('is_scheduled', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Choreographer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cast', models.ForeignKey(to='companies.Cast')),
            ],
            options={
                'ordering': ['member'],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group')),
                ('logo', models.ImageField(upload_to=b'companies')),
                ('short_description', models.CharField(max_length=255)),
                ('listserv', models.EmailField(max_length=254, blank=True)),
                ('has_schedule', models.BooleanField(default=False)),
                ('conflicts_due', models.DateTimeField(null=True, blank=True)),
                ('casting_due', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='Founder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('api_user', models.CharField(max_length=255)),
                ('api_key', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('client_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('cast', models.ManyToManyField(to='companies.Cast', blank=True)),
            ],
            options={
                'ordering': ['first_name', 'username'],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Rehearsal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(verbose_name=b'Start Time')),
                ('end_time', models.TimeField(verbose_name=b'End Time')),
                ('day_of_week', models.CharField(default=b'Mon', max_length=3, choices=[(b'Mon', b'Monday'), (b'Tue', b'Tuesday'), (b'Wed', b'Wednesday'), (b'Thu', b'Thursday'), (b'Fri', b'Friday'), (b'Sat', b'Saturday'), (b'Sun', b'Sunday')])),
                ('place', models.CharField(max_length=200)),
                ('is_scheduled', models.BooleanField(default=False)),
                ('company', models.ForeignKey(to='companies.Company')),
            ],
            options={
                'ordering': ['day_of_week', 'start_time'],
            },
        ),
        migrations.AddField(
            model_name='choreographer',
            name='company',
            field=models.ForeignKey(to='companies.Company'),
        ),
        migrations.AddField(
            model_name='choreographer',
            name='member',
            field=models.ForeignKey(to='companies.Member'),
        ),
        migrations.AddField(
            model_name='cast',
            name='company',
            field=models.ForeignKey(to='companies.Company'),
        ),
        migrations.AddField(
            model_name='cast',
            name='rehearsal',
            field=models.ForeignKey(blank=True, to='companies.Rehearsal', null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='company',
            field=models.ForeignKey(to='companies.Company'),
        ),
        migrations.AddField(
            model_name='admin',
            name='member',
            field=models.ForeignKey(to='companies.Member'),
        ),
        migrations.AddField(
            model_name='additionalrehearsals',
            name='cast',
            field=models.ForeignKey(to='companies.Cast'),
        ),
        migrations.AddField(
            model_name='additionalrehearsals',
            name='rehearsals',
            field=models.ManyToManyField(to='companies.Rehearsal'),
        ),
    ]
