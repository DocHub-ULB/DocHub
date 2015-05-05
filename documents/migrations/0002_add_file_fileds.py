# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

DEFAULT_IMG = "impossible_image"
DEFAULT_FILE = "impossibe_file"


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='file_type',
            field=models.CharField(default='', max_length=255),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='document',
            old_name='original',
            new_name='old_original_path'
        ),
        migrations.RenameField(
            model_name='document',
            old_name='pdf',
            new_name='old_pdf_path'
        ),
        ###########

        migrations.AddField(
            model_name='page',
            name='bitmap_120',
            field=models.ImageField(default=DEFAULT_IMG, width_field='height_120', upload_to='page_120'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='bitmap_600',
            field=models.ImageField(default=DEFAULT_IMG, width_field='height_600', upload_to='page_600'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='bitmap_900',
            field=models.ImageField(default=DEFAULT_IMG, width_field='height_900', upload_to='page_900'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='original',
            field=models.FileField(upload_to='original_document', default=DEFAULT_FILE),
        ),
        migrations.AddField(
            model_name='document',
            name='pdf',
            field=models.FileField(upload_to='pdf_document', default=DEFAULT_FILE),
        ),
        migrations.AlterField(
            model_name='page',
            name='height_120',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='height_600',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='height_900',
            field=models.PositiveIntegerField(default=0, null=True),
        ),

    ]
