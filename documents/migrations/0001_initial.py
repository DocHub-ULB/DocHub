# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import polydag.behaviors


class Migration(migrations.Migration):

    dependencies = [
        ('polydag', '__first__'),
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
                ('original', models.CharField(default='', max_length=2048)),
                ('pdf', models.CharField(default='', max_length=2048)),
                ('state', models.CharField(default='PREPARING', max_length=20)),
                ('md5', models.CharField(default='', max_length=32)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(polydag.behaviors.OneParent, 'polydag.taggable'),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('taggable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polydag.Taggable')),
                ('numero', models.IntegerField()),
                ('height_120', models.IntegerField()),
                ('height_600', models.IntegerField()),
                ('height_900', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(polydag.behaviors.OneParent, 'polydag.taggable'),
        ),
    ]
