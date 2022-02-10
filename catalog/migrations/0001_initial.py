from django.db import migrations, models

import mptt.fields


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255, db_index=True)),
                ("slug", models.SlugField()),
                ("description", models.TextField(null=True)),
                ("lft", models.PositiveIntegerField(editable=False, db_index=True)),
                ("rght", models.PositiveIntegerField(editable=False, db_index=True)),
                ("tree_id", models.PositiveIntegerField(editable=False, db_index=True)),
                ("level", models.PositiveIntegerField(editable=False, db_index=True)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="children",
                        blank=True,
                        to="catalog.Category",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
                "verbose_name_plural": "categories",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255, db_index=True)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField(null=True)),
                ("categories", models.ManyToManyField(to="catalog.Category")),
            ],
            options={
                "ordering": ["slug"],
            },
            bases=(models.Model,),
        ),
    ]
