# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_auto_20150523_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='document',
            field=models.ForeignKey(to='documents.Document', null=True),
            preserve_default=True,
        ),
    ]
