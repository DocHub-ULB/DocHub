from django.contrib import admin

from .models import CatalogEdition, Category, Course


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


@admin.register(CatalogEdition)
class CatalogEditionAdmin(admin.ModelAdmin):
    list_display = ("key", "academic_year", "status")
