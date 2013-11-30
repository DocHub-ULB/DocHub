from __future__ import unicode_literals

from default import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Install some prod apps ? Logging ?
INSTALLED_APPS += (
	'gunicorn',
)

ULB_LOGIN = 'https://www.ulb.ac.be/commons/intranet?_prt=ulb:facultes:sciences:p402&_ssl=on&_appl=http%253A%252F%252Fcours.urlab.be%252Fauth%253F&_prtm=redirect'

# DATABASES = {
#     'default': {
#         'ENGINE':'django.db.backends.postgresql_psycopg2',
#         'NAME': 'mydatabase',
#         'USER': 'mydatabaseuser',
#         'PASSWORD': 'mypassword',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }