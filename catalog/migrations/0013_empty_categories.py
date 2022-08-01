from django.db import migrations, models


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0012_course_period"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
