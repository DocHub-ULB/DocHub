from django.contrib import admin

from .models import Category, Course


class CategoryInline(admin.TabularInline):
    model = Course.categories.through
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("slug", "name")
    search_fields = ("slug", "name", "description")
    raw_id_fields = ("categories",)

    inlines = [
        CategoryInline,
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("slug", "name")
