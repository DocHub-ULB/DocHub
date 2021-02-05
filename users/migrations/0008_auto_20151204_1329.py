from django.db import models, migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20151120_1429'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='inscription',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='edited',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
    ]
