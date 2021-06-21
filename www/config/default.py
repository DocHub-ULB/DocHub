import os

from www.config.django_defaults import *

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace


EMAIL_SUBJECT_PREFIX = "[DocHub] "

# User Profile Model
AUTH_USER_MODEL = 'users.User'

# Page to show after a syslogin
LOGIN_REDIRECT_URL = 'index'

# url to internal login
LOGIN_URL = '/login'

UPLOAD_DIR = join(MEDIA_ROOT, 'documents')

DOCUMENT_STORAGE = 'django.core.files.storage.FileSystemStorage'

BASE_URL = "https://dochub.be/"

# CELERY ---

task_serializer = "json"
accept_content = ['json', 'msgpack']
worker_prefetch_multiplier = 1  # Do not prefetch more than 1 task

# END CELERY ----

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
    'rest_framework',
    'mptt',
    'django_js_reverse',
    'webpack_loader',
    'rest_framework.authtoken',
    'django.contrib.postgres',
    'tailwind',
    'dochub',
)

TAILWIND_APP_NAME = 'dochub'

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
    'search'
)

# must be after everything
INSTALLED_APPS += (
    'actstream',
)

TEMPLATES[0]['OPTIONS']['context_processors'] += ( # NOQA
    'django.template.context_processors.request',
    'www.context_processors.raven',
    'www.context_processors.read_only',
)

STATIC_ROOT = 'collected_static'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


AUTHENTICATION_BACKENDS = (
    'users.authBackend.UlbCasBackend',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'www.rest_renderers.VaryBrowsableAPIRenderer',
    ),
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

READ_ONLY = False

REJECTED_FILE_FORMATS = (".zip", ".tar", ".gz", ".rar")
