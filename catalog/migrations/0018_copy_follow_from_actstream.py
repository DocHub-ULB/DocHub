from django.contrib.contenttypes.models import ContentType
from django.db import connection, migrations, models
from django.db.models import Count


def forwards(apps, schema_editor):
    Course = apps.get_model("catalog", "Course")
    course_type = ContentType.objects.get(app_label="catalog", model="course")
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT object_id, user_id FROM actstream_follow WHERE content_type_id = %s ORDER BY object_id",
            [course_type.pk],
        )
        rows = cursor.fetchall()

    print(f"We have {len(rows)} follow to process")
    course = None
    for course_id, user_id in rows:
        if not course or course.pk != course_id:
            course = Course.objects.filter(id=course_id).first()
        if not course:
            continue
        # print(course_id, user_id)
        course.followed_by.add(user_id)
        course.save()


def backwards(apps, schema_editor):
    Course = apps.get_model("catalog", "Course")
    for course in Course.objects.all():
        course.followed_by.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0017_remove_empty_orphan_courses"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
