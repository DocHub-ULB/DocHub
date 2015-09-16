# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20150613_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='hidden',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
