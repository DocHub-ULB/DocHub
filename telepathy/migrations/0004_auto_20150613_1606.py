# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0003_auto_20150613_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='placement',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
    ]
