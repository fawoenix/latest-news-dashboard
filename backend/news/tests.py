"""Tests for the News app."""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Article, Category, Source

# Use dummy cache for tests to avoid Redis dependency
TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


class CategoryModelTest(TestCase):
    """Test the Category model."""

    def test_str_representation(self):
        category = Category.objects.create(name="Technology", slug="technology")
        self.assertEqual(str(category), "Technology")


class SourceModelTest(TestCase):
    """Test the Source model."""

    def test_str_representation(self):
        source = Source.objects.create(source_id="bbc-news", name="BBC News")
        self.assertEqual(str(source), "BBC News")


@override_settings(CACHES=TEST_CACHES)
class ArticleAPITest(TestCase):
    """Test the Article API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Technology", slug="technology"
        )
        self.source = Source.objects.create(
            source_id="test-source", name="Test Source"
        )
        self.article = Article.objects.create(
            source=self.source,
            category=self.category,
            source_name="Test Source",
            title="Test Article",
            description="A test article description.",
            url="https://example.com/test-article",
            published_at="2026-01-01T00:00:00Z",
            country="us",
        )

    def test_article_list(self):
        """Test retrieving the article list."""
        url = reverse("news:article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail(self):
        """Test retrieving a single article."""
        url = reverse("news:article-detail", kwargs={"pk": self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Article")

    def test_category_list(self):
        """Test retrieving the category list."""
        url = reverse("news:category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_source_list(self):
        """Test retrieving the source list."""
        url = reverse("news:source-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_category(self):
        """Test filtering articles by category."""
        url = reverse("news:article-list")
        response = self.client.get(url, {"category": "technology"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search(self):
        """Test searching articles."""
        url = reverse("news:article-list")
        response = self.client.get(url, {"search": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
