# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from graph.models import Course as OldCourse


def copy_followed(apps, schema_editor):
    User = apps.get_model("users", "User")
    Course = apps.get_model("catalog", "Course")
    for user in User.objects.all():
        followed = map(lambda x: x.id, user.follow.all())
        c = OldCourse.objects.filter(id__in=followed)
        for oldcourse in c:
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
