from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telepathy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='edited',
            field=models.DateTimeField(auto_now=True, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thread',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thread',
            name='edited',
            field=models.DateTimeField(auto_now=True, auto_now_add=True),
            preserve_default=True,
        ),
    ]
