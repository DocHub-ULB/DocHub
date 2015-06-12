# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_copy_data'),
        ('documents', '0001_squashed_0011'),
    ]

    operations = [

        migrations.AddField(
            model_name='document',
            name='course',
            field=models.ForeignKey(to='catalog.Course', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='tmp_name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='tmp_id',
            field=models.IntegerField(default=0, verbose_name='tmp_id'),
            preserve_default=False,
        ),
    ]
