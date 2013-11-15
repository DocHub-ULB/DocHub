# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# settiiiingz \o/ The competent programmer is fully aware of the strictly
# limited size of his own skull; therefore he approaches the programming task
# in full humility, and among other things he avoids clever tricks like the
# plague. -- Edsger W. Dijkstra

from os import path
from re import sub


# Absolute path to the directory that hold the manage.py file
PROJECT_PATH = sub('/www$', '', path.abspath(path.split(__file__)[0]))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (('NullCorp', 'null@null.com'),)
MANAGERS = ADMINS

# User Profile Model
AUTH_PROFILE_MODULE = 'users.Profile'

# Page to show after a syslogin
LOGIN_REDIRECT_URL = '/zoidberg/home'

# url to internal login
LOGIN_URL = '/syslogin'

# handlebars fragments for javascript templating
FRAGMENTS_DIR = path.join(PROJECT_PATH, "templates/fragments")

# hack for nginx
FORCE_SCRIPT_NAME = ''

# Upload settings
UPLOAD_LOG = '/tmp/upload_log'
UPLOAD_DIR = '%s/static/documents' % PROJECT_PATH
PARSING_WORKERS = 2

# Notifications pack size
PACK_SIZE = 20

# ULB login, need to add the url to redirect at the end
ULB_LOGIN = 'https://www.ulb.ac.be/commons/intranet?_prt=ulb:facultes:sciences:p402&_ssl=on&_prtm=redirect&_appl='

# ULB authentificator, need 2 parameters : SID and UID
ULB_AUTH = 'https://www.ulb.ac.be/commons/check?_type=normal&_sid=%s&_uid=%s'

# Activate the search system
SEARCH_SYSTEM = False

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True

ugettext = lambda s: s

LANGUAGES = (
  ('fr', ugettext('French')),
  ('en', ugettext('English')),
)

USE_L10N = True

ROOT_URLCONF = 'www.urls'
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = ('%s/static/' % PROJECT_PATH,)
ALLOWED_INCLUDE_ROOTS = ('%s/templates' % PROJECT_PATH,)
TEMPLATE_DIRS = ( '%s/templates' % PROJECT_PATH,)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sql',
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    #'devserver',
    'fragments',
    'south',
    'calendar',
    'documents',
    'graph',
    'telepathy',
    'users',
    'www',
    'polydag',
    'notify'
)

SECRET_KEY = '+5pykO7KSA9YjY0--ZOIDBEEEIRG-iueKUyjTQfBhZn+'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'users.processors.user',
    'notify.processors.notify'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

try:
    from production import *
except ImportError:
    pass

try:
    from version import VERSION
except ImportError:
    VERSION = "dev"
