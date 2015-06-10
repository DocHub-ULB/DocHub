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

from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ('password', 'last_login', 'follow', 'moderated_nodes')
    readonly_fields = ('netid', )
    list_display = ('netid', 'name', 'is_staff', 'is_academic', 'is_representative')
    list_filter = ('is_staff', 'is_academic', 'is_representative', 'last_login')
    search_fields = ('netid', 'first_name', 'last_name')
