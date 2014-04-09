# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from config import *

# No not write anything here !
# Configuration must be written in www/config/
# 	- django_default.py if it is a non-project related setting
# 	- default.py if you want it to be for all instances of b402
# 	- dev.py if you want it to be for all dev instances
# 	- prod.py if you want it to be for all production instances
#
# If you want to configure something instance related, please write it
# in local.py.
# You can use production.py or dev.py as a template for local.py or just use
# 	from {dev,production} import *
# in local.py and then overwrite some values
#
# If local.py does not exist, configuration will be loaded from dev.py directly
