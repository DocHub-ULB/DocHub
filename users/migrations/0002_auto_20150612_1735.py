from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 12, 17, 35, 37, 132204, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inscription',
            name='edited',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 12, 17, 35, 39, 253439, tzinfo=utc), auto_now=True, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='edited',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 12, 17, 35, 41, 392639, tzinfo=utc), auto_now=True, auto_now_add=True),
            preserve_default=False,
        ),
    ]
