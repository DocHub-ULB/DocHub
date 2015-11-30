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
from .models import Document, DocumentError


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('size', 'pages', 'original', 'pdf', 'md5',)

    list_display = ('id', 'name', 'pages', 'views', 'downloads', 'state', 'user', 'file_type')
    list_filter = ('state', 'created', 'edited', 'file_type')
    search_fields = ('md5', 'name')


@admin.register(DocumentError)
class DocumentErrorAdmin(admin.ModelAdmin):
    list_display = ('exception', 'document', 'task_id')
