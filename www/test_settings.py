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

from config import *

CELERY_ALWAYS_EAGER = True # Skip the Celery daemon

# all tasks will be executed locally by blocking until the task returns.
# apply_async() and Task.delay() will return an EagerResult instance,
# which emulates the API and behavior of AsyncResult,
# except the result is already evaluated.

import tempfile
UPLOAD_DIR = tempfile.mkdtemp()
