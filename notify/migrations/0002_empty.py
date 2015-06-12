# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def remove_notifs(apps, schema_editor):
    Notification = apps.get_model("notify", "Notification")
    PreNotification = apps.get_model("notify", "PreNotification")
    Notification.objects.all().delete()
    PreNotification.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_notifs),
    ]
