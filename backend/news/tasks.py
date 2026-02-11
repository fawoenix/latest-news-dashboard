"""
Celery tasks for periodic news fetching.

The `fetch_and_store_news` task is scheduled via Celery Beat
(see CELERY_BEAT_SCHEDULE in settings.py) to run every 30 minutes.
It fetches top headlines for all supported categories and stores them.
"""

import logging

from celery import shared_task

from .services import NEWS_API_CATEGORIES, NewsAPIService

logger = logging.getLogger("news")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_and_store_news(self):
    """
    Periodic task: fetch top headlines for every category and store them.

    Retries up to 3 times with a 60-second delay on failure.
    """
    service = NewsAPIService()
    total = 0

    for category in NEWS_API_CATEGORIES:
        try:
            count = service.fetch_top_headlines(category=category, country="us")
            total += count
            logger.info(
                "[Celery] Fetched %d articles for category=%s", count, category
            )
        except Exception as exc:
            logger.error(
                "[Celery] Error fetching category=%s: %s", category, exc
            )
            # Only retry on the last category failure to avoid flooding
            if category == NEWS_API_CATEGORIES[-1]:
                raise self.retry(exc=exc)

    logger.info("[Celery] Total articles fetched in this run: %d", total)
    return total
