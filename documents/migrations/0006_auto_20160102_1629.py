from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0005_auto_20151204_1329"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="course",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                verbose_name="Cours",
                to="catalog.Course",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="hidden",
            field=models.BooleanField(default=False, verbose_name="Est cach\xe9"),
        ),
        migrations.AlterField(
            model_name="document",
            name="name",
            field=models.CharField(max_length=255, verbose_name="Titre"),
        ),
        migrations.AlterField(
            model_name="document",
            name="state",
            field=models.CharField(
                default="PREPARING",
                max_length=20,
                verbose_name="\xc9tat",
                db_index=True,
                choices=[
                    ("PREPARING", "En pr\xe9paration"),
                    ("READY_TO_QUEUE", "Pr\xeat \xe0 \xeatre ajout\xe9 \xe0 Celery"),
                    ("IN_QUEUE", "Envoy\xe9 \xe0 Celery"),
                    ("PROCESSING", "En cours de traitement"),
                    ("DONE", "Rendu fini"),
                    ("ERROR", "Erreur"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="tags",
            field=models.ManyToManyField(to="tags.Tag", blank=True),
        ),
        migrations.AlterField(
            model_name="document",
            name="user",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                verbose_name="Utilisateur",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
