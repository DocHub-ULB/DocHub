# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django import template
from django.contrib.markup.templatetags.markup import markdown

register = template.Library()

@register.filter(name='markdown',is_safe=True)
def custommarkdownfilter(text):
    # TODO : check if this is safe or di we need "safe" to be added ?
    # Maybe rewrite markdown to be more flexible
    return markdown(text,"extra,codehilite,headerid(level=2),sane_lists")