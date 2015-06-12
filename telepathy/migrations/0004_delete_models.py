# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0002_thread_placement'),
        ('notify', '0002_empty'),
    ]

    operations = [
        migrations.DeleteModel(name="Message"),
        migrations.DeleteModel(name="Thread"),
    ]
