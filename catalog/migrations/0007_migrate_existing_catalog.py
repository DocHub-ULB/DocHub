from django.db import migrations


def assign_existing_catalog(apps, schema_editor):
    CatalogEdition = apps.get_model("catalog", "CatalogEdition")
    Category = apps.get_model("catalog", "Category")

    if (
        Category.objects.filter(
            is_archive=False,
            parents__is_archive=True,
        ).exists()
        or Category.objects.filter(
            is_archive=True,
            parents__is_archive=False,
        ).exists()
    ):
        raise RuntimeError(
            "The archived and current catalog trees unexpectedly overlap; adjust this migration manually."
        )

    archived_categories = Category.objects.filter(is_archive=True)
    if archived_categories.exists():
        archive_roots = archived_categories.filter(slug="archives")
        if archive_roots.count() != 1:
            raise RuntimeError(
                "The historical catalog does not have exactly one Archives root."
            )
        historical = CatalogEdition.objects.create(
            key="2018-2019",
            academic_year="2018-2019",
            status="archived",
        )
        archived_categories.update(edition=historical)
        archive_root = archive_roots.get()
        archive_root.name = "ULB"
        archive_root.save(update_fields=["name"])
        archive_root.parents.clear()

    current_categories = Category.objects.filter(is_archive=False)
    if current_categories.exists():
        if not current_categories.filter(slug="ULB").exists():
            raise RuntimeError(
                "The active catalog does not have the expected ULB root; adjust this migration manually."
            )
        current = CatalogEdition.objects.create(
            key="2023-2024",
            academic_year="2023-2024",
            status="active",
        )
        current_categories.update(edition=current)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0006_catalog_editions")]

    operations = [
        migrations.RunPython(assign_existing_catalog, migrations.RunPython.noop),
    ]
