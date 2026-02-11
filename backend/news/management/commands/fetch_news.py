"""
Management command to fetch news from the News API.

Usage:
    python manage.py fetch_news
    python manage.py fetch_news --category technology --country gb
    python manage.py fetch_news --query "artificial intelligence"
    python manage.py fetch_news --all-categories
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from news.services import NEWS_API_CATEGORIES, NewsAPIService


class Command(BaseCommand):
    help = "Fetch latest news from the News API and store in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            type=str,
            default="general",
            help="News category (business, entertainment, general, health, "
            "science, sports, technology).",
        )
        parser.add_argument(
            "--country",
            type=str,
            default="us",
            help="Country code (ISO 3166-1 alpha-2, e.g. us, gb, de).",
        )
        parser.add_argument(
            "--query",
            type=str,
            default=None,
            help="Search keyword for the /everything endpoint.",
        )
        parser.add_argument(
            "--all-categories",
            action="store_true",
            help="Fetch news for all supported categories.",
        )

    def handle(self, *args, **options):
        if settings.NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
            raise CommandError(
                "NEWS_API_KEY is not set. Export it as an environment variable:\n"
                "  export NEWS_API_KEY=your_api_key_here"
            )

        service = NewsAPIService()
        total = 0

        if options["all_categories"]:
            for cat in NEWS_API_CATEGORIES:
                self.stdout.write(f"Fetching category: {cat} ...")
                try:
                    count = service.fetch_top_headlines(
                        category=cat, country=options["country"]
                    )
                    total += count
                    self.stdout.write(
                        self.style.SUCCESS(f"  → {count} articles stored.")
                    )
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  → Error: {e}"))
        else:
            self.stdout.write(f"Fetching category: {options['category']} ...")
            try:
                count = service.fetch_top_headlines(
                    category=options["category"], country=options["country"]
                )
                total += count
                self.stdout.write(
                    self.style.SUCCESS(f"  → {count} articles stored.")
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  → Error: {e}"))

        if options["query"]:
            self.stdout.write(
                f"Fetching everything for query: {options['query']} ..."
            )
            try:
                count = service.fetch_everything(query=options["query"])
                total += count
                self.stdout.write(
                    self.style.SUCCESS(f"  → {count} articles stored.")
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  → Error: {e}"))

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! Total new articles: {total}")
        )
