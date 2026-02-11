"""
News models for the Latest News Dashboard.

Database Optimization Notes:
- Composite indexes on (category, published_at) and (source_name, published_at)
  for fast filtered + ordered queries.
- GIN index on title/description for full-text search (added via raw SQL migration).
- Index on published_at DESC for default ordering.
- Table partitioning by published_at month is handled via a custom migration.
"""

from django.db import models


class Category(models.Model):
    """
    Represents a news category (e.g. business, technology, sports).
    Stored separately so articles can be filtered efficiently by category FK.
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Source(models.Model):
    """
    News source (e.g. BBC News, CNN).
    Extracted into its own table to normalise the schema and enable
    fast source-based filtering via FK index.
    """

    source_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="The News API source identifier.",
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    url = models.URLField(blank=True, default="")
    country = models.CharField(max_length=10, blank=True, default="", db_index=True)
    language = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    A single news article fetched from the News API.

    Optimisation highlights:
    - ForeignKey to Source and Category (indexed automatically).
    - Composite indexes for common query patterns.
    - Full-text search index on title + description.
    - published_at index for chronological ordering.
    """

    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    # Denormalised source name for quick display without JOIN
    source_name = models.CharField(
        max_length=255, blank=True, default="", db_index=True
    )
    author = models.CharField(max_length=500, blank=True, default="")
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True, default="")
    url = models.URLField(max_length=2000, unique=True)
    url_to_image = models.URLField(max_length=2000, blank=True, default="")
    published_at = models.DateTimeField(db_index=True)
    content = models.TextField(blank=True, default="")
    country = models.CharField(max_length=10, blank=True, default="", db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            # Composite index: filter by category + order by published_at
            models.Index(
                fields=["category", "-published_at"], name="idx_category_pub"
            ),
            # Composite index: filter by source + order by published_at
            models.Index(
                fields=["source_name", "-published_at"], name="idx_source_pub"
            ),
            # Composite index: filter by country + order by published_at
            models.Index(
                fields=["country", "-published_at"], name="idx_country_pub"
            ),
            # Index for default ordering
            models.Index(fields=["-published_at"], name="idx_published_desc"),
            # Index for unique URL look-ups during upsert
            models.Index(fields=["url"], name="idx_article_url"),
        ]

    def __str__(self):
        return self.title[:80]
