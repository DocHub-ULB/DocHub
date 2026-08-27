import django.db.models.deletion
from django.db import migrations, models


def rename_historical_root(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    historical_root = Category.objects.filter(
        edition__key="2018-2019",
        slug="archives",
    ).first()
    if historical_root is not None:
        historical_root.slug = "ULB"
        historical_root.save(update_fields=["slug"])


def restore_historical_root_slug(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    historical_root = Category.objects.filter(
        edition__key="2018-2019",
        slug="ULB",
    ).first()
    if historical_root is not None:
        historical_root.slug = "archives"
        historical_root.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("catalog", "0007_migrate_existing_catalog")]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="edition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="categories",
                to="catalog.catalogedition",
            ),
        ),
        migrations.AddConstraint(
            model_name="catalogedition",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "active")),
                fields=("status",),
                name="one_active_catalog_edition",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(db_index=True, max_length=255),
        ),
        migrations.RunPython(rename_historical_root, restore_historical_root_slug),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=("edition", "slug"),
                name="unique_category_slug_per_edition",
            ),
        ),
    ]
