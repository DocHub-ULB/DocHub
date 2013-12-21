from __future__ import unicode_literals

from django_defaults import *

# User Profile Model
AUTH_PROFILE_MODULE = 'users.Profile'

# Page to show after a syslogin
LOGIN_REDIRECT_URL = '/zoidberg/home'

# url to internal login
LOGIN_URL = '/syslogin'

# handlebars fragments for javascript templating
FRAGMENTS_DIR = join(BASE_DIR, "templates/fragments")

# Upload settings
PROCESSING_DIR = '/tmp/processing'

UPLOAD_LOG = '/tmp/upload_log'
UPLOAD_DIR = '%s/static/documents' % BASE_DIR
PARSING_WORKERS = 2

# Notifications pack size
PACK_SIZE = 20

# ULB login, need to add the url to redirect at the end
ULB_LOGIN = 'https://www.ulb.ac.be/commons/intranet?_prt=ulb:facultes:sciences:p402&_ssl=on&_prtm=redirect&_appl='

# ULB authentificator, need 2 parameters : SID and UID
ULB_AUTH = 'https://www.ulb.ac.be/commons/check?_type=normal&_sid=%s&_uid=%s'

# Activate the search system
SEARCH_SYSTEM = False

#CELERY_BACKEND = 'django://'
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']

# libs
INSTALLED_APPS += (
    'django.contrib.humanize',
    'fragments',
    'south',
    'djcelery',
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

TEMPLATE_CONTEXT_PROCESSORS = (
    'users.processors.user',
    'notify.processors.notify',
)