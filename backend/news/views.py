"""
Views for the News API endpoints.

Implements:
- ArticleListView: paginated list with filters (category, source, country, search)
- ArticleDetailView: single article detail
- CategoryListView: all categories with article counts
- SourceListView: all sources with article counts
- FetchNewsView: manually trigger news fetching

Caching is applied to list views to reduce database load.
"""

import logging

from django.conf import settings
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, Category, Source
from .serializers import (
    ArticleListSerializer,
    ArticleSerializer,
    CategorySerializer,
    SourceSerializer,
)
from .services import NewsAPIService

logger = logging.getLogger("news")


class ArticleListView(generics.ListAPIView):
    """
    GET /api/news/articles/

    Returns a paginated list of news articles (50 per page).
    Supports filtering by:
      - category (slug)
      - source (source_id)
      - country (ISO 3166-1 alpha-2)
      - search (full-text search on title and description)

    Results are cached for 10 minutes to reduce database load.
    """

    serializer_class = ArticleListSerializer

    def get_queryset(self):
        """Build an optimised queryset with select_related and filters."""
        # Use select_related to prevent N+1 queries, defer heavy content field
        queryset = (
            Article.objects
            .select_related("category", "source")
            .defer("content")  # Skip heavy content field
            .order_by("-published_at")  # Explicit ordering for index usage
        )

        # --- Filter by category slug ---
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)

        # --- Filter by source ---
        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source__source_id=source)

        # --- Filter by country ---
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(country__iexact=country)

        # --- Full-text search on title & description ---
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ArticleDetailView(generics.RetrieveAPIView):
    """
    GET /api/news/articles/<id>/

    Returns full details for a single article.
    """

    queryset = Article.objects.select_related("category", "source").all()
    serializer_class = ArticleSerializer


class CategoryListView(generics.ListAPIView):
    """
    GET /api/news/categories/

    Returns all categories with article counts.
    Cached for 15 minutes.
    """

    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        return Category.objects.annotate(
            article_count=Count("articles")
        ).order_by("name")

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SourceListView(generics.ListAPIView):
    """
    GET /api/news/sources/

    Returns all sources with article counts.
    Cached for 15 minutes.
    """

    serializer_class = SourceSerializer
    pagination_class = None

    def get_queryset(self):
        return Source.objects.annotate(
            article_count=Count("articles")
        ).order_by("name")

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FetchNewsView(APIView):
    """
    POST /api/news/fetch/

    Manually trigger a news fetch from the News API.
    Accepts optional body parameters:
      - category: e.g. technology, business
      - country: e.g. us, gb
      - query: keyword search
    """

    def post(self, request):
        category = request.data.get("category", "general")
        country = request.data.get("country", "us")
        query = request.data.get("query", None)

        if settings.NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
            return Response(
                {
                    "error": "NEWS_API_KEY is not configured. "
                    "Set it in your environment variables."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        service = NewsAPIService()
        try:
            count = service.fetch_top_headlines(
                category=category, country=country
            )
            if query:
                count += service.fetch_everything(query=query)
            return Response(
                {"message": f"Successfully fetched and stored {count} articles."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error("Error fetching news: %s", e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
