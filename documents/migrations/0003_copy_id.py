# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def copy_id(apps, schema_editor):
    Document = apps.get_model("documents", "Document")

    for doc in Document.objects.all():
        doc.tmp_id = doc.id
        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_add_course_and_tmp_name'),
    ]

    operations = [
        migrations.RunPython(copy_id),
    ]
