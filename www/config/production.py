# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from default import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Install some prod apps
# eg : sentry, graphite, analytics, ...
INSTALLED_APPS += (
    'gunicorn',
)

AUTH_URL = "http%253A%252F%252Fdochub.be%252Fauth%253F"
ULB_LOGIN = (
    'https://www.ulb.ac.be/commons/intranet?' +
    '_prt=ulb:facultes:sciences:p402&_ssl=on' +
    '&_prtm=redirect' +
    '&_appl=' + AUTH_URL
)

# CELERY_BROKER = 'amqp://guest@localhost//'

# DATABASES = {
#     'default': {
#         'ENGINE':'django.db.backends.postgresql_psycopg2',
#         'NAME': 'mydatabase',
#         'USER': 'mydatabaseuser',
#     }
# }


# AWS_ACCESS_KEY_ID = "sfdsqdgsg"
# AWS_SECRET_ACCESS_KEY = "fsdfqsfs"
# BOTO_S3_BUCKET = "dochub-production"
# BOTO_S3_HOST = "filehost.example.com"

# DOCUMENT_STORAGE = 'django_boto.s3.storage.S3Storage'
