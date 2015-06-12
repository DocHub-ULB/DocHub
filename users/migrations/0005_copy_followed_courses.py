# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from graph.models import Course as OldCourse
from catalog.models import Course
from users.models import User


def copy_followed(apps, schema_editor):
    for user in User.objects.all():
        followed = user.follow.instance_of(OldCourse)
        for oldcourse in followed:
            newcourse = Course.objects.get(slug=oldcourse.slug)
            user.tmp_followed_courses.add(newcourse)

        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20150611_1539'),
    ]

    operations = [
        migrations.RunPython(copy_followed),
    ]
