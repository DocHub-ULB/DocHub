# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_moderated_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='moderated_courses',
            field=models.ManyToManyField(to='catalog.Course', blank=True),
            preserve_default=True,
        ),
    ]
