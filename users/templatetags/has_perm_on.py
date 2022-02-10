# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django import template

register = template.Library()


def has_perm_on(user, obj):
    """Does `user` has write permission on `obj` ?"""
    return user.write_perm(obj=obj)


register.filter("has_perm_on", has_perm_on)
