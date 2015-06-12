# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_tmp_name_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='id',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='tmp_id',
            new_name='id',
        ),
    ]
