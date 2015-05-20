# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_delete_original_fileds'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(max_length=255)),
                ('exception', models.CharField(max_length=1000)),
                ('traceback', models.TextField()),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
