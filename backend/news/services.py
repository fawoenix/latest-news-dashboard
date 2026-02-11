"""
News API service layer.

Handles communication with the external News API (https://newsapi.org).
Responsible for fetching articles and upserting them into the database.
"""

import logging
from datetime import datetime
from typing import Optional

import requests
from django.conf import settings
from django.utils.text import slugify

from .models import Article, Category, Source

logger = logging.getLogger("news")

# Categories supported by the News API top-headlines endpoint
NEWS_API_CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology",
]


class NewsAPIService:
    """
    Service class that wraps the News API.

    Methods:
        fetch_top_headlines – fetch top headlines by category / country.
        fetch_everything   – search all articles by keyword.
    """

    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = settings.NEWS_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": self.api_key})

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def fetch_top_headlines(
        self,
        category: str = "general",
        country: str = "us",
        page_size: int = 100,
    ) -> int:
        """
        Fetch top headlines from the News API and store them.

        Args:
            category: News category (business, entertainment, general, etc.).
            country: ISO 3166-1 alpha-2 country code.
            page_size: Number of results per request (max 100).

        Returns:
            Number of new articles stored.
        """
        url = f"{self.base_url}/top-headlines"
        params = {
            "category": category,
            "country": country,
            "pageSize": page_size,
        }

        logger.info(
            "Fetching top headlines: category=%s, country=%s", category, country
        )
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            raise ValueError(
                f"News API error: {data.get('message', 'Unknown error')}"
            )

        articles = data.get("articles", [])
        count = self._store_articles(articles, category=category, country=country)
        logger.info(
            "Stored %d articles for category=%s, country=%s", count, category, country
        )
        return count

    def fetch_everything(
        self,
        query: str,
        page_size: int = 100,
        sort_by: str = "publishedAt",
    ) -> int:
        """
        Search all articles using the News API /everything endpoint.

        Args:
            query: Keywords to search for.
            page_size: Number of results per request (max 100).
            sort_by: Sort order (relevancy, popularity, publishedAt).

        Returns:
            Number of new articles stored.
        """
        url = f"{self.base_url}/everything"
        params = {
            "q": query,
            "pageSize": page_size,
            "sortBy": sort_by,
        }

        logger.info("Fetching everything: query=%s", query)
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            raise ValueError(
                f"News API error: {data.get('message', 'Unknown error')}"
            )

        articles = data.get("articles", [])
        count = self._store_articles(articles)
        logger.info("Stored %d articles for query=%s", count, query)
        return count

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _store_articles(
        self,
        articles: list[dict],
        category: Optional[str] = None,
        country: Optional[str] = None,
    ) -> int:
        """
        Upsert a list of raw article dicts from the News API into the DB.

        Uses get_or_create on URL to avoid duplicates.

        Returns:
            Number of newly created articles.
        """
        created_count = 0

        # Resolve or create the category
        category_obj = None
        if category:
            category_obj, _ = Category.objects.get_or_create(
                slug=slugify(category),
                defaults={"name": category.title()},
            )

        for raw in articles:
            try:
                # Skip articles without a URL (they can't be linked)
                article_url = raw.get("url")
                if not article_url:
                    continue

                # Resolve or create the source
                source_info = raw.get("source", {})
                source_obj = self._get_or_create_source(source_info, country)

                # Parse published date
                published_at = self._parse_date(raw.get("publishedAt"))
                if not published_at:
                    continue

                # Upsert article
                _, created = Article.objects.get_or_create(
                    url=article_url,
                    defaults={
                        "source": source_obj,
                        "category": category_obj,
                        "source_name": source_info.get("name", ""),
                        "author": (raw.get("author") or "")[:500],
                        "title": (raw.get("title") or "")[:1000],
                        "description": raw.get("description") or "",
                        "url_to_image": raw.get("urlToImage") or "",
                        "published_at": published_at,
                        "content": raw.get("content") or "",
                        "country": country or "",
                    },
                )
                if created:
                    created_count += 1

            except Exception as e:
                logger.warning("Skipping article: %s", e)
                continue

        return created_count

    @staticmethod
    def _get_or_create_source(
        source_info: dict, country: Optional[str] = None
    ) -> Optional[Source]:
        """Get or create a Source record from News API source dict."""
        source_id = source_info.get("id")
        source_name = source_info.get("name", "Unknown")

        if not source_id:
            # Use a slugified name as fallback ID
            source_id = slugify(source_name) or "unknown"

        source_obj, _ = Source.objects.get_or_create(
            source_id=source_id,
            defaults={
                "name": source_name,
                "country": country or "",
            },
        )
        return source_obj

    @staticmethod
    def _parse_date(date_string: Optional[str]) -> Optional[datetime]:
        """Parse an ISO 8601 date string from the News API."""
        if not date_string:
            return None
        try:
            # News API returns dates like "2024-01-15T10:30:00Z"
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
