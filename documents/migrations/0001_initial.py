from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0001_initial"),
        ("tags", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("size", models.PositiveIntegerField(default=0, null=True)),
                ("words", models.PositiveIntegerField(default=0, null=True)),
                ("pages", models.PositiveIntegerField(default=0, null=True)),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("views", models.PositiveIntegerField(default=0, null=True)),
                ("downloads", models.PositiveIntegerField(default=0, null=True)),
                ("file_type", models.CharField(default="", max_length=255)),
                ("original", models.FileField(upload_to="original_document")),
                ("pdf", models.FileField(upload_to="pdf_document")),
                (
                    "state",
                    models.CharField(default="PREPARING", max_length=20, db_index=True),
                ),
                ("md5", models.CharField(default="", max_length=32, db_index=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="catalog.Course",
                        null=True,
                    ),
                ),
                ("tags", models.ManyToManyField(to="tags.Tag")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DocumentError",
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
                ("task_id", models.CharField(max_length=255)),
                ("exception", models.CharField(max_length=1000)),
                ("traceback", models.TextField()),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="documents.Document"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Page",
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
                ("numero", models.IntegerField(db_index=True)),
                (
                    "bitmap_120",
                    models.ImageField(width_field="height_120", upload_to="page_120"),
                ),
                (
                    "bitmap_600",
                    models.ImageField(width_field="height_600", upload_to="page_600"),
                ),
                (
                    "bitmap_900",
                    models.ImageField(width_field="height_900", upload_to="page_900"),
                ),
                ("height_120", models.PositiveIntegerField(default=0, null=True)),
                ("height_600", models.PositiveIntegerField(default=0, null=True)),
                ("height_900", models.PositiveIntegerField(default=0, null=True)),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="documents.Document"
                    ),
                ),
            ],
            options={
                "ordering": ["numero"],
            },
            bases=(models.Model,),
        ),
    ]
