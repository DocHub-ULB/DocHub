# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0010_page_id_is_primary'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['numero']},
        ),
        migrations.AlterField(
            model_name='document',
            name='md5',
            field=models.CharField(default='', max_length=32, db_index=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='state',
            field=models.CharField(default='PREPARING', max_length=20, db_index=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='numero',
            field=models.IntegerField(db_index=True),
        ),
    ]
