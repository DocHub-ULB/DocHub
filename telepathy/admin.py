from django.contrib import admin

from .models import Message, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'user', 'created', 'document')
    list_filter = ('created', 'edited')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'user', 'created', 'edited')
    list_filter = ('created', 'edited')
