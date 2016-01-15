# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_auto_20160102_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='bitmap_120',
            field=models.ImageField(height_field='height_120', upload_to='page_120'),
        ),
        migrations.AlterField(
            model_name='page',
            name='bitmap_600',
            field=models.ImageField(height_field='height_600', upload_to='page_600'),
        ),
        migrations.AlterField(
            model_name='page',
            name='bitmap_900',
            field=models.ImageField(height_field='height_900', upload_to='page_900'),
        ),
    ]
