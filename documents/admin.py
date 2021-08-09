from django.conf import settings
from django.contrib import admin
from django.db.models.query import QuerySet

from .models import Document, DocumentError, Vote


def reprocess(modeladmin, request, queryset: 'QuerySet[Document]'):
    if settings.READ_ONLY:
        raise Exception("Documents are read-only.")

    for doc in queryset:
        doc.reprocess(force=True)


reprocess.short_description = "Reprocess selected documents" # type: ignore


def autotag(modeladmin, request, queryset: 'QuerySet[Document]'):
    for doc in queryset:
        doc.tag_from_name()


autotag.short_description = "Auto-tag selected documents" # type: ignore


def repair(modeladmin, request, queryset: 'QuerySet[Document]'):
    if settings.READ_ONLY:
        raise Exception("Documents are read-only.")

    for doc in queryset:
        doc.repair()


repair.short_description = "Repair selected documents" # type: ignore


class VoteInline(admin.StackedInline):
    readonly_fields = ["when"]
    raw_id_fields = ('user',)
    extra = 1
    model = Vote

    fieldsets = (
        (None, {
            "fields": (
                ("user", "vote_type", "when"),
            ),
        }),
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'document')
    list_display = ('document', 'user', 'vote_type', 'when')

    list_filter = ('vote_type', 'when')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('size', 'pages', 'original', 'pdf', 'md5', 'state',)
    filter_horizontal = ('tags',)
    date_hierarchy = 'created'

    list_display = ('id', 'name', 'pages', 'views', 'downloads', 'hidden', 'state', 'created', 'user', 'file_type', 'imported')
    list_filter = ('state', 'created', 'edited', 'file_type',)
    search_fields = ('md5', 'name', 'user__netid')
    raw_id_fields = ('user', 'course')

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
                'import_source',
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
