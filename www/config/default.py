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

from django_defaults import *

EMAIL_SUBJECT_PREFIX = "[DocHub] "

# User Profile Model
AUTH_USER_MODEL = 'users.User'

# Page to show after a syslogin
LOGIN_REDIRECT_URL = 'index'

# url to internal login
LOGIN_URL = '/'

UPLOAD_DIR = join(MEDIA_ROOT, 'documents')

DOCUMENT_STORAGE = 'django.core.files.storage.FileSystemStorage'

BASE_URL = "http://dochub.be/"

# ULB login, need to add the url to redirect at the end
ULB_LOGIN = 'https://www.ulb.ac.be/commons/intranet?_prt=ulb:facultes:sciences:p402&_ssl=on&_prtm=redirect&_appl='

# Activate the search system
SEARCH_SYSTEM = False


CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERYD_PREFETCH_MULTIPLIER = 1  # Do not prefetch more than 1 task

# Activate identicons
IDENTICON = True

# libs
INSTALLED_APPS += (
    'django.contrib.humanize',
    'django.contrib.admin',
    'djcelery',
    'rest_framework',
    'mptt',
    'analytical',
    'pipeline',
)

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

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATIC_ROOT = 'collected_static'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
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
}

ACTSTREAM_SETTINGS = {
    'USE_JSONFIELD': True,
}

PIWIK_DOMAIN_PATH = 'piwik.urlab.be'
PIWIK_SITE_ID = '1'


PIPELINE = {
    'COMPILERS': ('react.utils.pipeline.JSXCompiler', ),
}

PIPELINE['JAVASCRIPT'] = {
    '3party': {
        'source_filenames': (
            '3party/jquery/jquery.js',
            '3party/foundation/js/foundation.min.js',
            '3party/markdown/markdown.js',
            '3party/moment/moment-with-locales.js',
            '3party/react/react.js',
            '3party/react/react-dom.js',
            '3party/mathjax/mathjax.js',
            '3party/select/js/select2.js',
            '3party/select/js/i18n/fr.js',
            '3party/cookie/cookie.js'
        ),
        'output_filename': '3party.js',
    },
    'main': {
        'source_filenames': (
            'scripts/viewer.js',
            'scripts/main.js',
            'scripts/tree.jsx',
        ),
        'output_filename': 'main.js',
    }
}

PIPELINE['STYLESHEETS'] = {
    '3party': {
        'source_filenames': (
            '3party/foundation/css/normalize.css',
            '3party/foundation/css/foundation.css',
            '3party/foundation-icons/foundation-icons.css',
            '3party/select/css/select2.css',
        ),
        'output_filename': '3party.css',
    },
    'main': {
        'source_filenames': (
            'style/main.css',
            'style/viewer.css',
        ),
        'output_filename': 'main.css',
    },
}
