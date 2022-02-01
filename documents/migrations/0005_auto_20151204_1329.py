from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0004_document_hidden"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="edited",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
