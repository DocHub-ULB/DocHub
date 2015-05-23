# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_page_is_no_node'),
    ]

    operations = [
        migrations.RunSQL(
            """ALTER TABLE ONLY documents_page
            ALTER COLUMN id
            SET DEFAULT nextval('documents_page_id_seq'::regclass);"""
        ),
    ]
