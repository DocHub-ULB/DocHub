# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polydag', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polydag.Node')),
                ('slug', models.SlugField()),
                ('description', models.TextField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name_plural': 'categories',
            },
            bases=('polydag.node',),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polydag.Node')),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(null=True)),
            ],
            options={
                'ordering': ['slug'],
            },
            bases=('polydag.node',),
        ),
        migrations.CreateModel(
            name='CourseInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('infos', models.TextField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(to='graph.Course', unique=True)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
    ]
