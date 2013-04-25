# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.db import models
from polydag.models import Node
from graph.models import Course


class Event(Node):
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(auto_now=True)
    information = models.TextField()
