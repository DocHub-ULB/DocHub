from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-id']},
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together={('user', 'action')},
        ),
    ]
