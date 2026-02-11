"""
URL configuration for the News app.

All endpoints are prefixed with /api/news/ (configured in backend/urls.py).
"""

from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    # Article endpoints
    path("articles/", views.ArticleListView.as_view(), name="article-list"),
    path(
        "articles/<int:pk>/",
        views.ArticleDetailView.as_view(),
        name="article-detail",
    ),
    # Category & Source endpoints
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("sources/", views.SourceListView.as_view(), name="source-list"),
    # Manual fetch trigger
    path("fetch/", views.FetchNewsView.as_view(), name="fetch-news"),
]
