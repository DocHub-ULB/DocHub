# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import json

from catalog.models import Category, Course
from graph.models import Course as OldCourse


def generate_tree(apps, schema_editor):
    tree = json.load(open('parsing/tree.json'))
    root = Category.objects.create(name="ULB")
    walk(tree, root, apps)

    for course in Course.objects.all():
        old = OldCourse.objects.get(slug=course.slug)
        course.name = old.name
        course.description = old.description
        course.save()


def walk(jsonTree, parentNode, apps):

    for key in jsonTree:
        val = jsonTree[key]
        if key.lower() == 'course':
            for slug in val:
                c = Course.objects.get_or_create(slug=slug, defaults={'name': 'a'})[0]
                c.categories.add(parentNode)
                c.save()
        else:
            category = Category.objects.create(name=key, parent=parentNode)
            walk(val, category, apps)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_tree),
    ]
