# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from graph.models import Course as OldCourse
# from catalog.models import Course


def attach_doc_to_course(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    Course = apps.get_model("catalog", "Course")

    for doc in Document.objects.all():
        parent = OldCourse.objects.get(_children=doc)
        course = Course.objects.get(slug=parent.slug)
        doc.course = course
        doc.tmp_name = doc.name
        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_copy_data'),
        ('documents', '0002_add_course_and_tmp_name'),
    ]

    operations = [
        migrations.RunPython(attach_doc_to_course),
    ]
