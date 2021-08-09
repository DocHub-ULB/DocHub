from django.contrib import admin

from .models import Category, Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('slug', 'name', 'description')
    raw_id_fields = ("categories",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'level')
    search_fields = ('slug', 'parent__name', 'parent__slug')
    list_filter = ('level',)
