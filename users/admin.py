# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
