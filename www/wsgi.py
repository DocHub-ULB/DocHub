# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'
application = get_wsgi_application()
