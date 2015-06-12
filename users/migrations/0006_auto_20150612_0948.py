# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_copy_followed_courses'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='tmp_followed_courses',
            new_name='followed_courses',
        ),
    ]
