from django.db import migrations, models


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0012_course_period"),
    ]

    operations = [
        # We do not empty the categories as we want to keep the old tree
        # while we don't have a way to migrate documents to the new courses
        # grep OLD_TREE to find other places we have done tricks to keep the old tree
        # migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
