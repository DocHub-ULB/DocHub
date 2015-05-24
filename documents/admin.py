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
from .models import Document, DocumentError


class DocumentAdmin(admin.ModelAdmin):
    fields = ('name', 'user', 'size', 'pages', 'views', 'downloads', 'state')
    readonly_fields = (
        'size',
        'pages',
    )

    list_display = ('id', 'name', 'pages', 'views', 'downloads', 'state', 'user', )
    list_filter = ('state',)
    search_fields = ('md5', 'name')

admin.site.register(Document, DocumentAdmin)


class DocumentErrorAdmin(admin.ModelAdmin):
    list_display = ('exception', 'document', 'task_id')

admin.site.register(DocumentError, DocumentErrorAdmin)
