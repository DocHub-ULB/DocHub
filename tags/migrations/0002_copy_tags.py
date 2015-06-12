# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from polydag.models import Keyword


def copy(apps, schema_editor):
    Tag = apps.get_model("tags", "Tag")

    for key in Keyword.objects.all():
        Tag.objects.create(name=key.name)


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy),
    ]
