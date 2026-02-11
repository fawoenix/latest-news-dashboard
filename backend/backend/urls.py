"""
Root URL configuration for the Latest News Dashboard backend.

Includes:
- /admin/          – Django admin panel
- /api/news/       – News REST API endpoints
- /swagger/        – Swagger UI documentation
- /redoc/          – ReDoc documentation
"""

from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Swagger / OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="Latest News Dashboard API",
        default_version="v1",
        description="API for fetching and managing news articles from the News API.",
        contact=openapi.Contact(email="admin@lamia-news.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/news/", include("news.urls", namespace="news")),
    # API Documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
