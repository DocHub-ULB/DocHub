from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0002_auto_20150612_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='placement',
            field=models.TextField(default=None, blank=True),
            preserve_default=True,
        ),
    ]
