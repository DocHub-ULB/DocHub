# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_document_is_no_node'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='tmp_name',
            new_name='name',
        ),
    ]
