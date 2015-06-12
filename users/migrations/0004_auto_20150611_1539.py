# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_link_documents'),
        ('users', '0003_user_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='moderated_nodes',
        ),
        migrations.AddField(
            model_name='user',
            name='tmp_followed_courses',
            field=models.ManyToManyField(to='catalog.Course'),
            preserve_default=True,
        ),
    ]
