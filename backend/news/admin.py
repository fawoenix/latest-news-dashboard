"""Admin configuration for the News app models."""

from django.contrib import admin

from .models import Article, Category, Source


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "source_id", "country", "language")
    search_fields = ("name", "source_id")
    list_filter = ("country", "language")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source_name", "category", "published_at", "country")
    search_fields = ("title", "description")
    list_filter = ("category", "country", "published_at")
    date_hierarchy = "published_at"
    raw_id_fields = ("source", "category")
