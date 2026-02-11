#!/usr/bin/env python
import os
import sys
import django
import time

# Setup Django
sys.path.insert(0, '/home/sohaib/Desktop/dev/lamia/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from news.models import Article

print("Testing database query performance...")
start = time.time()
articles = list(Article.objects.select_related('category', 'source').defer('content').order_by('-published_at')[:50])
elapsed = time.time() - start

print(f"✓ Fetched {len(articles)} articles in {elapsed:.3f} seconds")
print(f"First article: {articles[0].title if articles else 'No articles'}")
