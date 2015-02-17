# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=140, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Taggable',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polydag.Node')),
                ('year', models.CharField(max_length=9, db_index=True)),
                ('keywords', models.ManyToManyField(to='polydag.Keyword', db_index=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('polydag.node',),
        ),
        migrations.AddField(
            model_name='node',
            name='_children',
            field=models.ManyToManyField(to='polydag.Node', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_polydag.node_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
