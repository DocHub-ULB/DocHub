# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import polydag.behaviors


class Migration(migrations.Migration):

    replaces = [
        ('documents', '0001_initial'),
        ('documents', '0002_add_file_fileds'),
        ('documents', '0003_write_type_move_files'),
        ('documents', '0004_delete_original_fileds'),
        ('documents', '0005_add_documenterror'),
        ('documents', '0006_auto_20150523_1547'),
        ('documents', '0007_page_document'),
        ('documents', '0008_fill_page_document'),
        ('documents', '0009_page_is_no_node'),
        ('documents', '0010_page_id_is_primary'),
        ('documents', '0011_auto_20150524_1441')
    ]

    dependencies = [
        ('polydag', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('taggable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polydag.Taggable')),
                ('description', models.TextField(blank=True)),
                ('size', models.PositiveIntegerField(default=0, null=True)),
                ('words', models.PositiveIntegerField(default=0, null=True)),
                ('pages', models.PositiveIntegerField(default=0, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('views', models.PositiveIntegerField(default=0, null=True)),
                ('downloads', models.PositiveIntegerField(default=0, null=True)),
                ('file_type', models.CharField(default='', max_length=255)),
                ('original', models.FileField(upload_to='original_document')),
                ('pdf', models.FileField(upload_to='pdf_document')),
                ('state', models.CharField(default='PREPARING', max_length=20, db_index=True)),
                ('md5', models.CharField(default='', max_length=32, db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(polydag.behaviors.OneParent, 'polydag.taggable'),
        ),
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
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.IntegerField(db_index=True)),
                ('bitmap_120', models.ImageField(width_field='height_120', upload_to='page_120')),
                ('bitmap_600', models.ImageField(width_field='height_600', upload_to='page_600')),
                ('bitmap_900', models.ImageField(width_field='height_900', upload_to='page_900')),
                ('height_120', models.PositiveIntegerField(default=0, null=True)),
                ('height_600', models.PositiveIntegerField(default=0, null=True)),
                ('height_900', models.PositiveIntegerField(default=0, null=True)),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
                'ordering': ['numero'],
            },
            bases=(models.Model,),
        ),
    ]
