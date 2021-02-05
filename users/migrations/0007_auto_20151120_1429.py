from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20151120_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notify_on_new_doc',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='notify_on_new_thread',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='notify_on_response',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
