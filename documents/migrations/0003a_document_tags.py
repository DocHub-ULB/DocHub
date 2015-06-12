# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_copy_tags'),
        ('documents', '0003_copy_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(to='tags.Tag'),
            preserve_default=True,
        ),
    ]
