# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_is_is_primary'),
        ('telepathy', '0005_readd_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='document',
            field=models.ForeignKey(to='documents.Document', null=True),
            preserve_default=True,
        ),
    ]
