# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Document, DocumentError, Vote


def reprocess(modeladmin, request, queryset):
    for doc in queryset:
        doc.reprocess(force=True)


reprocess.short_description = "Reprocess selected documents"


def autotag(modeladmin, request, queryset):
    for doc in queryset:
        doc.tag_from_name()


autotag.short_description = "Auto-tag selected documents"


def repair(modeladmin, request, queryset):
    for doc in queryset:
        doc.repair()


repair.short_description = "Repair selected documents"


class VoteInline(admin.StackedInline):
    readonly_fields = ["when"]
    extra = 1
    model = Vote

    fieldsets = (
        (None, {
            "fields": (
                ("user", "vote_type", "when"),
            ),
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('size', 'pages', 'original', 'pdf', 'md5', 'state',)
    filter_horizontal = ('tags',)

    list_display = ('id', 'name', 'pages', 'views', 'downloads', 'hidden', 'state', 'created', 'user', 'file_type')
    list_filter = ('state', 'created', 'edited', 'file_type')
    search_fields = ('md5', 'name')
    inlines = [VoteInline]

    actions = (reprocess, autotag, repair)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                ('course', 'user'),
                ('pages', 'state'),
                'hidden',
                'tags',
                'description',
            )
        }),
        ('Extra', {
            'fields': (
                ('file_type', 'md5'),
                ('original', 'pdf'),
                ('views', 'downloads'),
            )
        })
    )


@admin.register(DocumentError)
class DocumentErrorAdmin(admin.ModelAdmin):
    list_display = ('exception', 'document', 'task_id')
