# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0008_fill_page_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='taggable_ptr',
        ),
        migrations.AddField(
            model_name='page',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='page',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
    ]
