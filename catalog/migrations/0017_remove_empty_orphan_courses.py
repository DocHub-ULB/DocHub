from django.db import migrations, models
from django.db.models import Count


def forwards(apps, schema_editor):
    Course = apps.get_model("catalog", "Course")
    empty_orphans = Course.objects.annotate(
        docs=Count("document", distinct=True), cats=Count("categories", distinct=True)
    ).filter(docs=0, cats=0)
    empty_orphans.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0016_alter_category_type_courseuserview"),
    ]

    operations = [
        migrations.RunSQL(sql="DROP TABLE IF EXISTS telepathy_message"),
        migrations.RunSQL(sql="DROP TABLE IF EXISTS telepathy_thread"),
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
