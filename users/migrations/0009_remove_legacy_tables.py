from django.db import migrations

LEGACY_TABLES = [
    "actstream_action",
    "actstream_follow",
    "authtoken_token",
]


def remove_legacy_tables(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        for table in LEGACY_TABLES:
            if vendor == "sqlite":
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            else:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_user_moderator_welcome_dismissed"),
    ]

    operations = [
        migrations.RunPython(remove_legacy_tables, migrations.RunPython.noop),
    ]
