import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0009_category_type"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Old table name from checking with sqlmigrate, new table
                # name from AuthorBook._meta.db_table.
                migrations.RunSQL(
                    sql="ALTER TABLE catalog_course_categories RENAME TO catalog_coursecategory",
                    reverse_sql="ALTER TABLE catalog_coursecategory RENAME TO catalog_course_categories",
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="CourseCategory",
                    fields=[
                        (
                            "id",
                            models.AutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "category",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to="catalog.category",
                            ),
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name="course",
                    name="categories",
                    field=models.ManyToManyField(
                        through="catalog.CourseCategory", to="catalog.category"
                    ),
                ),
                migrations.AddField(
                    model_name="coursecategory",
                    name="course",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="catalog.course"
                    ),
                ),
            ],
        ),
    ]
