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
from .models import Course, Category


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('slug', 'name')
    # filter_horizontal = ('categories',)
    raw_id_fields = ("categories",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'level')
    list_filter = ('level',)
