"""
Serializers for the News API endpoints.

These serializers handle the conversion between Article/Source/Category
model instances and JSON representations used by the REST API.
"""

from rest_framework import serializers

from .models import Article, Category, Source


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""

    article_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "article_count"]


class SourceSerializer(serializers.ModelSerializer):
    """Serializer for the Source model."""

    article_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Source
        fields = [
            "id",
            "source_id",
            "name",
            "description",
            "url",
            "country",
            "language",
            "article_count",
        ]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.
    Includes nested source and category names for display convenience.
    """

    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )
    source_detail = SourceSerializer(source="source", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "source_name",
            "source_detail",
            "category_name",
            "author",
            "title",
            "description",
            "url",
            "url_to_image",
            "published_at",
            "content",
            "country",
            "created_at",
        ]


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for article list views.
    Omits heavy fields like content to reduce payload size.
    """

    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "source_name",
            "category_name",
            "author",
            "title",
            "description",
            "url",
            "url_to_image",
            "published_at",
            "country",
        ]
