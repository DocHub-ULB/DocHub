# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


import os
from www import settings


def write_type(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    for doc in Document.objects.all():
        doc.file_type = os.path.splitext(doc.old_original_path)[1].lower()
        doc.save()


def move_documents(apps, schema_editor):
    try:
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "original_document"))
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "pdf_document"))
    except OSError as e:
        if e.errno != 17:
            raise e

    Document = apps.get_model("documents", "Document")
    for doc in Document.objects.all():
        new_original = os.path.join("original_document", str(uuid.uuid4()) + doc.file_type)
        try:
            os.rename(doc.old_original_path, os.path.join(settings.MEDIA_ROOT, new_original))
        except OSError as e:
            print "Document {} failed (l33) : renaming {} to {}. Skipping.".format(
                doc.id,
                doc.old_original_path,
                os.path.join(settings.MEDIA_ROOT, new_original)
            )
        doc.original.name = new_original

        if doc.file_type != ".pdf":
            new_pdf = os.path.join("pdf_document", str(uuid.uuid4()) + ".pdf")
            try:
                os.rename(doc.old_pdf_path, os.path.join(settings.MEDIA_ROOT, new_pdf))
            except OSError as e:
                print "Document {} failed (l45) : renaming {} to {}. Skipping.".format(
                    doc.id,
                    doc.old_pdf_path,
                    os.path.join(settings.MEDIA_ROOT, new_pdf)
                )
            doc.pdf.name = new_pdf
        else:
            doc.pdf = doc.original

        doc.save()


def move_pages(apps, schema_editor):
    try:
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "page_900"))
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "page_600"))
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "page_120"))
    except OSError as e:
        if e.errno != 17:
            raise e

    Node = apps.get_model("polydag", "Node")
    Page = apps.get_model("documents", "Page")
    Document = apps.get_model("documents", "Document")

    for doc in Document.objects.all():
        parent = Node.objects.filter(_children=doc).get()
        dir = os.path.join(settings.UPLOAD_DIR, str(parent.id), "doc-{}/images/".format(doc.id))

        node = Node.objects.get(id=doc.id)
        page_set = Page.objects.filter(id__in=map(lambda x: x.id, node._children.all()))

        for page in page_set:
            new_900 = os.path.join("page_900", str(uuid.uuid4()) + ".jpg")
            new_600 = os.path.join("page_600", str(uuid.uuid4()) + ".jpg")
            new_120 = os.path.join("page_120", str(uuid.uuid4()) + ".jpg")

            try:
                os.rename(dir + "{:0>6}_{}.jpg".format(page.numero, 'b'), os.path.join(settings.MEDIA_ROOT, new_900))
                os.rename(dir + "{:0>6}_{}.jpg".format(page.numero, 'n'), os.path.join(settings.MEDIA_ROOT, new_600))
                os.rename(dir + "{:0>6}_{}.jpg".format(page.numero, 'm'), os.path.join(settings.MEDIA_ROOT, new_120))
            except OSError as e:
                print e
                print "Page {} (doc {}) failed at img move".format(page.id, doc.id)

            page.bitmap_900.name = new_900
            page.bitmap_600.name = new_600
            page.bitmap_120.name = new_120

            page.save()

        doc.save()


def del_dirs(apps, schema_editor):
    old_path = os.path.join(settings.MEDIA_ROOT, "documents")
    left = sum([len(files) for r, d, files in os.walk(old_path)])
    if left != 0:
        print "{} is not empty ({} files left). Skipping.".format(old_path, left)
    else:
        for dir, _, _ in reversed(list(os.walk(old_path))):
            try:
                os.removedirs(dir)
            except OSError as e:
                if e.errno != 2:
                    raise e


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_add_file_fileds'),
    ]

    operations = [
        migrations.RunPython(write_type),
        migrations.RunPython(move_documents),
        migrations.RunPython(move_pages),
        migrations.RunPython(del_dirs),
    ]
