from __future__ import unicode_literals

from default import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'django_extensions',
    'kombu.transport.django',  # celery_broker
    # Remove devserver : recursion error with django 1.6
    # See https://code.djangoproject.com/ticket/21348
    #'devserver',
)

CELERY_BROKER = 'django://'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(BASE_DIR, 'db.sqlite'),
    }
}
