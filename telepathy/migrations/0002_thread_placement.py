# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='placement',
            field=models.TextField(default=None, null=True),
            preserve_default=True,
        ),
    ]
