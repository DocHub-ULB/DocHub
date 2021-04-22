# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django import template

from users.authBackend import NetidBackend

register = template.Library()


@register.simple_tag(name='login_url')
def login_url(next=""):
    return NetidBackend.login_url()
