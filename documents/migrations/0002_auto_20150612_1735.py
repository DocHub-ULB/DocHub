import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 12, 17, 35, 33, 575805, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='edited',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 12, 17, 35, 35, 465436, tzinfo=utc), auto_now=True, auto_now_add=True),
            preserve_default=False,
        ),
    ]
