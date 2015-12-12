# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_document_hidden'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
