"""
Management command to warm up the Redis cache with frequently accessed data.
This preloads categories, sources, and the first page of articles into cache.

Usage:
    python manage.py warmup_cache
"""

from django.core.management.base import BaseCommand
from django.test.client import RequestFactory
from news.views import ArticleListView, CategoryListView, SourceListView


class Command(BaseCommand):
    help = "Warm up Redis cache with frequently accessed data"

    def handle(self, *args, **options):
        self.stdout.write("Warming up cache...")
        factory = RequestFactory()

        # Warm up categories
        self.stdout.write("  - Caching categories...")
        request = factory.get("/api/news/categories/", HTTP_HOST="localhost:8000")
        view = CategoryListView.as_view()
        response = view(request)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS(f"    ✓ Cached {len(response.data)} categories"))
        else:
            self.stdout.write(self.style.ERROR(f"    ✗ Failed: {response.status_code}"))

        # Warm up sources
        self.stdout.write("  - Caching sources...")
        request = factory.get("/api/news/sources/", HTTP_HOST="localhost:8000")
        view = SourceListView.as_view()
        response = view(request)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS(f"    ✓ Cached {len(response.data)} sources"))
        else:
            self.stdout.write(self.style.ERROR(f"    ✗ Failed: {response.status_code}"))

        # Warm up first page of articles (most accessed)
        self.stdout.write("  - Caching first page of articles...")
        request = factory.get("/api/news/articles/?page=1", HTTP_HOST="localhost:8000")
        view = ArticleListView.as_view()
        response = view(request)
        if response.status_code == 200:
            self.stdout.write(
                self.style.SUCCESS(
                    f"    ✓ Cached {len(response.data['results'])} articles (page 1)"
                )
            )
        else:
            self.stdout.write(self.style.ERROR(f"    ✗ Failed: {response.status_code}"))

        self.stdout.write(self.style.SUCCESS("\n✓ Cache warmup complete!"))
