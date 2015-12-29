# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
