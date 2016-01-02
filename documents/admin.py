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


def reprocess(modeladmin, request, queryset):
    for doc in queryset:
        doc.reprocess(force=True)

reprocess.short_description = "Reprocess selected documents"


def autotag(modeladmin, request, queryset):
    for doc in queryset:
        doc.tag_from_name()

autotag.short_description = "Auto-tag selected documents"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('size', 'pages', 'original', 'pdf', 'md5', 'state',)
    filter_horizontal = ('tags',)

    list_display = ('id', 'name', 'pages', 'views', 'downloads', 'state', 'user', 'file_type')
    list_filter = ('state', 'created', 'edited', 'file_type')
    search_fields = ('md5', 'name')

    actions = (reprocess, autotag,)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                ('course', 'user'),
                ('pages', 'state', 'hidden'),
                'tags',
                'description',
            )
        }),
        ('Extra', {
            'classes': ('collapse',),
            'fields': (
                ('file_type', 'md5'),
                ('original', 'pdf'),
                ('views', 'downloads')
            )
        })
    )


@admin.register(DocumentError)
class DocumentErrorAdmin(admin.ModelAdmin):
    list_display = ('exception', 'document', 'task_id')
