# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polydag', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_polydag.node_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
