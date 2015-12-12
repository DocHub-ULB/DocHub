# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0004_auto_20150613_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
