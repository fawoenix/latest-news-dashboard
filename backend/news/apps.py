from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for the news application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "news"
    verbose_name = "News Articles"
