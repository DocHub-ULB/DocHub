import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0005_alter_course_period")]

    operations = [
        migrations.CreateModel(
            name="CatalogEdition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(max_length=32, unique=True)),
                (
                    "academic_year",
                    models.CharField(blank=True, max_length=9, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("archived", "Archived")],
                        max_length=8,
                    ),
                ),
            ],
            options={"ordering": ["key"]},
        ),
        migrations.AddField(
            model_name="category",
            name="edition",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="categories",
                to="catalog.catalogedition",
            ),
        ),
    ]
