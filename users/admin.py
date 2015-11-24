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

from django.contrib import admin
from .models import User, Inscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ('password',)
    readonly_fields = ('netid', 'last_login')
    list_display = ('netid', 'name', 'is_staff', 'is_academic', 'is_representative', 'last_login', 'created')
    list_filter = ('is_staff', 'is_academic', 'is_representative', 'last_login', 'created')
    search_fields = ('netid', 'first_name', 'last_name')


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('user', )
    list_display = ('id', 'user', 'faculty', 'section', 'year')
    list_filter = ('faculty', 'section', 'year')
    search_fields = ('section', )
