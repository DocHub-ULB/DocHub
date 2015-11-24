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

from __future__ import absolute_import

try:
    from .local import *
except ImportError:
    try:
        from .dev import *
    except ImportError as e:
        raise Exception("Failed to import from dev or local, are the files present? exception: %s" % e)

try:
    DEBUG
    TEMPLATE_DEBUG
    DATABASES['default']
    CELERY_BROKER
    if not DEBUG:
        EMAIL_HOST
        SERVER_EMAIL
        ADMINS
        MANAGERS
        ALLOWED_HOSTS
except NameError as e:
    raise NameError('Required config values not found: %s. Abort !' % e)
