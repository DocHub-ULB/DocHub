# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def copy(apps, schema_editor):
    Tag = apps.get_model("tags", "Tag")
    Document = apps.get_model("documents", "Document")

    for doc in Document.objects.all():
        for kw in doc.keywords.all():
            tag = Tag.objects.get(name=kw.name)
            doc.tags.add(tag)
            doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003a_document_tags'),
    ]

    operations = [
        migrations.RunPython(copy),
    ]
