# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django_defaults import *

EMAIL_SUBJECT_PREFIX = "[DocHub] "

# User Profile Model
AUTH_USER_MODEL = 'users.User'

# Page to show after a syslogin
LOGIN_REDIRECT_URL = 'index'

# url to internal login
LOGIN_URL = '/'

# handlebars fragments for javascript templating
FRAGMENTS_DIR = join(BASE_DIR, "templates/fragments")

# Upload settings
PROCESSING_DIR = '/tmp/processing'
TMP_UPLOAD_DIR = "/tmp/p402-upload/"

UPLOAD_LOG = '/tmp/upload_log'
UPLOAD_DIR = join(MEDIA_ROOT, 'documents')


# ULB login, need to add the url to redirect at the end
ULB_LOGIN = 'https://www.ulb.ac.be/commons/intranet?_prt=ulb:facultes:sciences:p402&_ssl=on&_prtm=redirect&_appl='

# ULB authentificator, need 2 parameters : SID and UID
ULB_AUTH = 'https://www.ulb.ac.be/commons/check?_type=normal&_sid=%s&_uid=%s'

# Activate the search system
SEARCH_SYSTEM = False

# CELERY_BACKEND = 'django://'
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERYD_PREFETCH_MULTIPLIER = 1  # Do not prefetch more than 1 task

# Activate identicons
IDENTICON = True

# libs
INSTALLED_APPS += (
    'django.contrib.humanize',
    'suit',  # Must be before admin
    'django.contrib.admin',
    'fragments',
    'djcelery',
    'compressor',
)

# apps
INSTALLED_APPS += (
    'www',
    'calendars',
    'documents',
    'graph',
    'telepathy',
    'users',
    'polydag',
    'notify',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'users.processors.user',
    'notify.processors.notify',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'Admin - DocHub',
    'MENU_EXCLUDE': (
        'auth',
        'djcelery',
    ),
}

COMPRESS_ROOT = join(BASE_DIR, "static")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_OFFLINE = True
