# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_write_type_move_files'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='old_pdf_path'
        ),
        migrations.RemoveField(
            model_name='document',
            name='old_original_path'
        )
    ]
