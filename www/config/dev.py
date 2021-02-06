# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from www.config.default import *  # noqa

DEBUG = True

MIDDLEWARE += ( # noqa
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += ( # noqa
    'django_extensions',
    'debug_toolbar',
)

BROKER_URL = 'redis://localhost:6379/0'
task_always_eager = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(BASE_DIR, 'db.sqlite'),  # noqa
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

AUTH_PASSWORD_VALIDATORS = []
