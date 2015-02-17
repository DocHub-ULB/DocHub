# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('polydag', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('netid', models.CharField(unique=True, max_length=20)),
                ('first_name', models.CharField(max_length=127)),
                ('last_name', models.CharField(max_length=127)),
                ('email', models.CharField(unique=True, max_length=255)),
                ('registration', models.CharField(max_length=80, blank=True)),
                ('photo', models.CharField(default='', max_length=10)),
                ('welcome', models.BooleanField(default=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_academic', models.BooleanField(default=False)),
                ('is_representative', models.BooleanField(default=False)),
                ('follow', models.ManyToManyField(related_name='followed', db_index=True, to='polydag.Node', blank=True)),
                ('moderated_nodes', models.ManyToManyField(to='polydag.Node', db_index=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('faculty', models.CharField(max_length=80, null=True)),
                ('section', models.CharField(max_length=80, null=True)),
                ('year', models.PositiveIntegerField(null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='inscription',
            unique_together=set([('user', 'section', 'faculty', 'year')]),
        ),
    ]
