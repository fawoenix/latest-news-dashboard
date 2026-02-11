# Latest News Dashboard — Project Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [How to Run the Project](#3-how-to-run-the-project)
4. [Setup Process](#4-setup-process)
   - 4.1 [System Requirements](#41-system-requirements)
   - 4.2 [PostgreSQL Setup](#42-postgresql-setup)
   - 4.3 [Redis Setup](#43-redis-setup-wsl)
   - 4.4 [Backend Setup](#44-backend-setup)
   - 4.5 [Frontend Setup](#45-frontend-setup)
5. [Database Design and Optimization](#5-database-design-and-optimization)
6. [Caching Strategy](#6-caching-strategy)
7. [API Documentation](#7-api-documentation)
8. [Background Tasks](#8-background-tasks)
9. [Project Structure](#9-project-structure)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview

The Latest News Dashboard is a full-stack web application that aggregates and displays news articles fetched from [NewsAPI](https://newsapi.org/). It is designed with a focus on performance through database optimization, response caching, and automated background processing.

**Core capabilities:**
- Fetches articles across multiple categories from NewsAPI
- Stores and deduplicates articles in PostgreSQL
- Serves articles via a RESTful API with filtering, search, and pagination
- Caches responses in Redis to reduce database load
- Runs periodic background tasks via Celery to fetch fresh news automatically
- Displays articles in a responsive Angular frontend

**Technology stack:**

| Layer | Technology |
|-------|------------|
| Frontend | Angular 19+ |
| Backend | Django 4.x, Django REST Framework |
| Database | PostgreSQL 14+ |
| Cache and Broker | Redis 7+ |
| Task Queue | Celery + Celery Beat |
| API Documentation | drf-yasg (Swagger / ReDoc) |

---

## 2. Architecture

```
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────┐
│   Angular App   │──────▶│  Django REST API      │──────▶│  PostgreSQL  │
│   (port 4200)   │ HTTP  │  (port 8000)          │       │  Database    │
└─────────────────┘       │                      │       └──────────────┘
                          │  ┌──────────────┐    │
                          │  │ Redis Cache   │    │       ┌──────────────┐
                          │  └──────────────┘    │──────▶│  News API    │
                          │  ┌──────────────┐    │       │ newsapi.org  │
                          │  │ Celery Worker │    │       └──────────────┘
                          │  │ (periodic)    │    │
                          │  └──────────────┘    │
                          └──────────────────────┘
```

**Request flow:**

1. The user interacts with the Angular frontend at port 4200.
2. Angular sends HTTP requests to the Django REST API at port 8000.
3. The API checks Redis for a cached response.
4. On a cache hit, the cached data is returned immediately.
5. On a cache miss, the API queries PostgreSQL, stores the result in Redis, then returns it.
6. Independently, Celery Beat triggers the Celery worker every 30 minutes to fetch new articles from NewsAPI and store them in PostgreSQL.

---

## 3. How to Run the Project

### Quick Start

Start each of the following in a separate terminal window.

**Terminal 1 — Redis (WSL):**
```bash
wsl
sudo service redis-server start
```

**Terminal 2 — Django Backend:**
```bash
cd backend
..\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Terminal 3 — Angular Frontend:**
```bash
cd frontend
npx ng serve
```

**Terminal 4 — Celery Worker (optional, for automatic news fetching):**
```bash
cd backend
..\venv\Scripts\Activate.ps1
celery -A backend worker --loglevel=info --pool=solo
```

**Terminal 5 — Celery Beat Scheduler (optional):**
```bash
cd backend
..\venv\Scripts\Activate.ps1
celery -A backend beat --loglevel=info
```

Once all services are running, open your browser at:
```
http://localhost:4200
```

---

## 4. Setup Process

### 4.1 System Requirements

**Operating system:** Windows 10 or Windows 11 with WSL2 enabled.

**Required software:**

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| PostgreSQL | 14+ | [postgresql.org](https://www.postgresql.org/download/windows/) |
| Git | Latest | [git-scm.com](https://git-scm.com/download/win) |
| WSL2 | — | Via PowerShell (see Redis setup) |

**Install WSL2** (required for Redis):
Open PowerShell as Administrator and run:
```powershell
wsl --install
```
Restart your computer when prompted.

---

### 4.2 PostgreSQL Setup

**Install PostgreSQL:**
1. Download the installer from [postgresql.org](https://www.postgresql.org/download/windows/).
2. Run the installer. Note the password you set for the `postgres` superuser.
3. Ensure PostgreSQL is added to your system PATH during installation.

**Create the database and user:**

Open a terminal and connect to PostgreSQL:
```bash
psql -U postgres
```

Run the following SQL commands:
```sql
CREATE USER db_user WITH PASSWORD 'your_db_password';
CREATE DATABASE news_dashboard OWNER db_user;
ALTER USER db_user CREATEDB;
\q
```

Replace `db_user` and `your_db_password` with values that match what you will put in your `.env` file.

**Verify the connection:**
```bash
psql -U db_user -d news_dashboard
```

---

### 4.3 Redis Setup (WSL)

Redis does not run natively on Windows. It must be installed and run inside WSL.

**Install Redis in WSL:**
```bash
wsl
sudo apt-get update
sudo apt-get install redis-server
```

**Start Redis:**
```bash
sudo service redis-server start
```

**Verify Redis is running:**
```bash
redis-cli ping
```
Expected output: `PONG`

**Note:** Redis must be started each time you open a new WSL session. It does not start automatically.

---

### 4.4 Backend Setup

**Step 1 — Clone the repository:**
```bash
git clone <REPOSITORY_URL>
cd news-dashboard
```

**Step 2 — Create and activate a virtual environment:**
```bash
cd backend
python -m venv ../venv
```

Activate it:
```powershell
# PowerShell
..\venv\Scripts\Activate.ps1

# Command Prompt
..\venv\Scripts\activate.bat
```

If PowerShell blocks the script, run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Step 3 — Install dependencies:**
```bash
pip install django djangorestframework psycopg2-binary django-redis ^
            requests django-cors-headers celery redis drf-yasg python-dotenv
```

Or if `requirements.txt` is present:
```bash
pip install -r requirements.txt
```

**Step 4 — Configure environment variables:**

Create the `.env` file from the example:
```bash
copy .env.example .env
```

Edit `backend/.env`:
```env
NEWS_API_KEY=your_newsapi_key_here

DB_NAME=news_dashboard
DB_USER=db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

Get a free News API key from [https://newsapi.org/](https://newsapi.org/).

The `.env` file is listed in `.gitignore` and will not be committed to version control.

**Step 5 — Apply database migrations:**
```bash
python manage.py migrate
```

**Step 6 — Fetch initial data:**
```bash
python manage.py fetch_news --all-categories
```

**Step 7 — (Optional) Create an admin user:**
```bash
python manage.py createsuperuser
```

**Step 8 — Start the server:**
```bash
python manage.py runserver
```

API available at: `http://localhost:8000`

---

### 4.5 Frontend Setup

**Step 1 — Install Node.js dependencies:**
```bash
cd frontend
npm install
```

**Step 2 — Start the development server:**
```bash
npx ng serve
```

Frontend available at: `http://localhost:4200`

---

## 5. Database Design and Optimization

### 5.1 Database Schema

The main model is `Article`, which stores fetched news articles.

```
Article
├── id              (auto primary key)
├── title           (CharField, max 500)
├── description     (TextField, nullable)
├── content         (TextField, nullable)
├── url             (URLField, unique)
├── url_to_image    (URLField, nullable)
├── published_at    (DateTimeField)
├── source_name     (CharField)
├── author          (CharField, nullable)
├── category        (CharField)
├── country         (CharField, 2 chars)
└── created_at      (DateTimeField, auto)
```

The unique constraint on `url` ensures articles are never duplicated during repeated fetches.

### 5.2 Indexing Strategy

| Index Type | Fields | Purpose |
|------------|--------|---------|
| B-tree | `published_at DESC` | Fast default ordering by date |
| Composite | `(category, published_at DESC)` | Category filter with date ordering |
| Composite | `(source_name, published_at DESC)` | Source filter with date ordering |
| Composite | `(country, published_at DESC)` | Country filter with date ordering |
| GIN trigram | `title` | Fast full-text ICONTAINS search |
| GIN trigram | `description` | Fast full-text ICONTAINS search |
| Unique | `url` | Deduplication during upsert |

These indexes are created in migration `0002_database_optimization.py`.

### 5.3 Table Partitioning

A partitioned archive table (`news_article_archive`) is used for older articles. It uses range partitioning on `published_at` with quarterly partitions. Articles older than 90 days can be moved to this table using the `archive_old_articles()` PostgreSQL function, keeping the main table lean for fast queries.

```sql
-- Archive old articles (run periodically)
SELECT archive_old_articles();
```

### 5.4 Query Optimizations

- `defer()` excludes the heavy `content` field from list queries, reducing data transfer.
- `select_related()` on category and source fields avoids N+1 query problems.
- A lightweight `ArticleListSerializer` is used for list views and omits the `content` field.
- `CONN_MAX_AGE=600` keeps database connections persistent across requests.
- `statement_timeout=30s` prevents runaway queries from blocking the database.

---

## 6. Caching Strategy

### 6.1 Cache Backend

Redis is used as the cache backend via `django-redis`. The cache is configured with pickle serialization and zlib compression to minimize memory usage.

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        }
    }
}
```

A connection pool of 100 connections with retry-on-timeout is configured to handle concurrent requests reliably.

### 6.2 What is Cached and for How Long

| Cache Target | TTL | Reason |
|--------------|-----|--------|
| Article list responses | 10 minutes | Reduces DB load for paginated queries |
| Category list | 15 minutes | Changes rarely |
| Source list | 15 minutes | Changes rarely |
| Django sessions | Default Redis TTL | Session data stored in Redis |

### 6.3 Cache Invalidation

Cached article list responses are invalidated when new articles are fetched, ensuring users see fresh data after background task runs.

**Manual cache clear:**
```bash
python manage.py shell
```
```python
from django.core.cache import cache
cache.clear()
exit()
```

**Cache warmup** (pre-populate cache after a clear):
```bash
python manage.py warmup_cache
```

---

## 7. API Documentation

### 7.1 Interactive Documentation

| URL | Description |
|-----|-------------|
| `http://localhost:8000/swagger/` | Swagger UI — interactive endpoint testing |
| `http://localhost:8000/redoc/` | ReDoc — clean reference documentation |
| `http://localhost:8000/admin/` | Django Admin panel |

---

### 7.2 Endpoints Reference

---

#### GET `/api/news/articles/`

Returns a paginated list of news articles. Supports filtering and full-text search.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number. Default: 1. Page size: 50. |
| `category` | string | No | Filter by category slug (e.g. `technology`, `sports`, `health`) |
| `source` | string | No | Filter by source ID (e.g. `bbc-news`, `cnn`) |
| `country` | string | No | Filter by 2-letter country code (e.g. `us`, `gb`) |
| `search` | string | No | Full-text search across title and description |

**Response:**
```json
{
  "count": 250,
  "next": "http://localhost:8000/api/news/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Article title here",
      "description": "Short description of the article.",
      "url": "https://source.com/article",
      "url_to_image": "https://source.com/image.jpg",
      "published_at": "2026-02-11T10:00:00Z",
      "source_name": "BBC News",
      "author": "Jane Smith",
      "category": "technology",
      "country": "gb"
    }
  ]
}
```

**Example requests:**
```bash
# All articles, first page
curl http://localhost:8000/api/news/articles/

# Filter by category
curl http://localhost:8000/api/news/articles/?category=technology

# Full-text search
curl http://localhost:8000/api/news/articles/?search=AI

# Combined filters
curl "http://localhost:8000/api/news/articles/?category=technology&search=AI&page=2"

# Filter by country and source
curl "http://localhost:8000/api/news/articles/?country=us&source=cnn"
```

---

#### GET `/api/news/articles/<id>/`

Returns the full details of a single article including the `content` field.

**URL Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | The article's ID |

**Response:**
```json
{
  "id": 1,
  "title": "Article title here",
  "description": "Short description.",
  "content": "Full article content...",
  "url": "https://source.com/article",
  "url_to_image": "https://source.com/image.jpg",
  "published_at": "2026-02-11T10:00:00Z",
  "source_name": "BBC News",
  "author": "Jane Smith",
  "category": "technology",
  "country": "gb",
  "created_at": "2026-02-11T10:05:00Z"
}
```

**Example:**
```bash
curl http://localhost:8000/api/news/articles/1/
```

---

#### GET `/api/news/categories/`

Returns all categories that have at least one article, along with article counts.

**Response:**
```json
[
  { "name": "business", "count": 45 },
  { "name": "entertainment", "count": 30 },
  { "name": "health", "count": 22 },
  { "name": "science", "count": 18 },
  { "name": "sports", "count": 60 },
  { "name": "technology", "count": 75 }
]
```

**Example:**
```bash
curl http://localhost:8000/api/news/categories/
```

---

#### GET `/api/news/sources/`

Returns all news sources that have at least one article, along with article counts.

**Response:**
```json
[
  { "name": "BBC News", "id": "bbc-news", "count": 40 },
  { "name": "CNN", "id": "cnn", "count": 35 },
  { "name": "TechCrunch", "id": "techcrunch", "count": 28 }
]
```

**Example:**
```bash
curl http://localhost:8000/api/news/sources/
```

---

#### POST `/api/news/fetch/`

Manually triggers a news fetch from NewsAPI. Useful for pulling fresh articles on demand without waiting for the Celery scheduler.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | No | Category to fetch (e.g. `technology`) |
| `country` | string | No | Country code to filter by (e.g. `us`) |
| `query` | string | No | Search keyword for NewsAPI |

**Example request body:**
```json
{
  "category": "technology",
  "country": "us",
  "query": "artificial intelligence"
}
```

**Response:**
```json
{
  "status": "success",
  "articles_fetched": 20,
  "duplicates_skipped": 3
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/news/fetch/ \
  -H "Content-Type: application/json" \
  -d "{\"category\": \"technology\", \"country\": \"us\"}"
```

---

### 7.3 Error Responses

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad request — invalid query parameter |
| 404 | Article not found |
| 500 | Internal server error |

**Example 404 response:**
```json
{
  "detail": "Not found."
}
```

---

## 8. Background Tasks

Celery is used to run periodic tasks without blocking the web server.

### 8.1 Celery Configuration

Celery is configured in `backend/celery.py` and uses Redis as the message broker. Celery Beat acts as a scheduler that triggers tasks at defined intervals.

### 8.2 Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `fetch_news_task` | Every 30 minutes | Fetches latest articles from NewsAPI for all categories |
| `cleanup_old_articles` | Daily at midnight | Archives articles older than 90 days |

### 8.3 Running Celery on Windows

Windows requires the `--pool=solo` flag for the Celery worker:

```bash
celery -A backend worker --loglevel=info --pool=solo
```

Run Celery Beat in a separate terminal:
```bash
celery -A backend beat --loglevel=info
```

### 8.4 Triggering Tasks Manually

```bash
python manage.py shell
```
```python
from news.tasks import fetch_news_task
fetch_news_task.delay(category='technology', country='us')
```

---

## 9. Project Structure

```
news-dashboard/
├── backend/
│   ├── backend/
│   │   ├── settings.py                    # Django settings
│   │   ├── urls.py                        # Root URL configuration
│   │   ├── celery.py                      # Celery configuration
│   │   └── wsgi.py                        # WSGI entry point
│   ├── news/
│   │   ├── models.py                      # Article, Category, Source models
│   │   ├── serializers.py                 # DRF serializers
│   │   ├── views.py                       # API views with caching
│   │   ├── urls.py                        # News app URL patterns
│   │   ├── services.py                    # NewsAPI service layer
│   │   ├── tasks.py                       # Celery periodic tasks
│   │   ├── admin.py                       # Django admin configuration
│   │   ├── tests.py                       # Unit tests
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── fetch_news.py          # CLI command to fetch news
│   │   └── migrations/
│   │       ├── 0001_initial.py
│   │       └── 0002_database_optimization.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                               # Environment variables (not committed)
│   └── .env.example                       # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── header/
│   │   │   │   ├── dashboard/
│   │   │   │   └── article-card/
│   │   │   ├── models/
│   │   │   │   └── news.model.ts
│   │   │   ├── services/
│   │   │   │   └── news.service.ts
│   │   │   ├── app.ts
│   │   │   ├── app.routes.ts
│   │   │   └── app.config.ts
│   │   └── styles.css
│   ├── angular.json
│   └── package.json
├── venv/
├── README.md
└── DOCUMENTATION.md
```

---

## 10. Troubleshooting

### PowerShell execution policy error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8000 already in use

```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Cannot connect to PostgreSQL

1. Open `services.msc` and verify the PostgreSQL service is running.
2. Confirm the credentials in `.env` match what you set during PostgreSQL setup.
3. Test directly: `psql -U db_user -d news_dashboard`

### Cannot connect to Redis

1. Open WSL and run: `sudo service redis-server start`
2. Verify: `redis-cli ping` — should return `PONG`

### Celery worker fails on Windows

Always use the `--pool=solo` flag:
```bash
celery -A backend worker --loglevel=info --pool=solo
```

### No articles showing in the frontend

Run the fetch command to populate the database:
```bash
python manage.py fetch_news --all-categories
```

### Module not found errors

Ensure your virtual environment is activated before running any Python commands:
```powershell
..\venv\Scripts\Activate.ps1
```

---

**Author:** Lamia Ben Salem
**Last updated:** February 2026
