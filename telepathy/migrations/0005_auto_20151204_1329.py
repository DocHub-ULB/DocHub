from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0004_auto_20150613_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
