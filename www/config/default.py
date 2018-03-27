# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from www.config.django_defaults import *

EMAIL_SUBJECT_PREFIX = "[DocHub] "

# User Profile Model
AUTH_USER_MODEL = 'users.User'

# Page to show after a syslogin
LOGIN_REDIRECT_URL = 'index'

# url to internal login
LOGIN_URL = '/'

UPLOAD_DIR = join(MEDIA_ROOT, 'documents')

DOCUMENT_STORAGE = 'django.core.files.storage.FileSystemStorage'

BASE_URL = "https://dochub.be/"

# ULB login, need to add the url to redirect at the end
ULB_LOGIN = 'https://www.ulb.ac.be/commons/intranet?_prt=ulb:facultes:sciences:p402&_ssl=on&_prtm=redirect&_appl='

# Activate the search system
SEARCH_SYSTEM = False


CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERYD_PREFETCH_MULTIPLIER = 1  # Do not prefetch more than 1 task

# Activate identicons
IDENTICON = True

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'scripts/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

# libs
INSTALLED_APPS += (
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.sites', # needed for sitemap
    'django.contrib.sitemaps',
    'djcelery',
    'rest_framework',
    'mptt',
    'django_js_reverse',
    'webpack_loader',
    'rest_framework.authtoken',
)

SITE_ID = 1

# apps
INSTALLED_APPS += (
    'www',
    'documents',
    'telepathy',
    'users',
    'catalog',
    'tags',
    'notifications',
)

# must be after everything
INSTALLED_APPS += (
    'actstream',
)

TEMPLATES[0]['OPTIONS']['context_processors'] += (
    'django.core.context_processors.request',
    'www.context_processors.raven',
)

STATIC_ROOT = 'collected_static'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


AUTHENTICATION_BACKENDS = (
    'users.authBackend.NetidBackend',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

ACTSTREAM_SETTINGS = {
    'USE_JSONFIELD': True,
}

JS_REVERSE_EXCLUDE_NAMESPACES = ['admin', 'djdt']

MAX_RENDER_PAGES = 100
