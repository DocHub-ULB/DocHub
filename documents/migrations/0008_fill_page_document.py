# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import sys


def fill_doc(apps, schema_editor):
    Page = apps.get_model("documents", "Page")
    Node = apps.get_model("polydag", "Node")
    Document = apps.get_model("documents", "Document")

    sys.stdout.write('\n    Printing a dot every 100 pages !\n    ')
    i = 0
    for page in Page.objects.all():
        i += 1
        if i % (80 * 100) == 0:
            sys.stdout.write('\n    ')
            sys.stdout.flush()
        if i % 100 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        possible = list(Node.objects.filter(_children=page).all())
        if len(possible) == 1:
            parent = possible[0]
            doc = Document.objects.get(id=parent.id)
            page.document = doc
            page.save()
        else:
            sys.stdout.write('x')
            sys.stdout.flush()
            page.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_page_document'),
    ]

    operations = [
        migrations.RunPython(fill_doc),
    ]
