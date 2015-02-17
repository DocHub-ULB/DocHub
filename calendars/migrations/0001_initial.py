# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polydag', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polydag.Node')),
                ('start', models.DateTimeField(auto_now=True)),
                ('end', models.DateTimeField(auto_now=True)),
                ('information', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('polydag.node',),
        ),
    ]
