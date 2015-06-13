# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150612_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='faculty',
            field=models.CharField(default='', max_length=80, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='section',
            field=models.CharField(default='', max_length=80, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='year',
            field=models.PositiveIntegerField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='comment',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
    ]
