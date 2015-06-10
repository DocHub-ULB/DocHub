# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_unique_on_inscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='created',
            field=models.DateTimeField(default=datetime.date(2015, 6, 10), auto_now_add=True),
            preserve_default=False,
        ),
    ]
