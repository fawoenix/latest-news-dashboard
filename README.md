# Latest News Dashboard

A full-stack web application that fetches and displays news from the [News API](https://newsapi.org/), built with **Django REST Framework** (backend), **Angular** (frontend), **PostgreSQL** (database), and **Redis** (caching).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup (Django)](#backend-setup-django)
4. [Frontend Setup (Angular)](#frontend-setup-angular)
5. [Database & Caching Setup](#database--caching-setup)
6. [Running the Application](#running-the-application)
7. [API Documentation](#api-documentation)
8. [Database Optimization](#database-optimization)
9. [Project Structure](#project-structure)

---

## Architecture Overview

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

---

## Prerequisites

| Tool        | Version | Purpose                         |
| ----------- | ------- | ------------------------------- |
| Python      | 3.10+   | Django backend runtime          |
| Node.js     | 18+     | Angular frontend runtime        |
| PostgreSQL  | 14+     | Primary database                |
| Redis       | 7+      | Caching & Celery message broker |
| Angular CLI | 19+     | Frontend build tooling          |

---

## Backend Setup (Django)

### 1. Create and activate a virtual environment

```bash
cd backend
python3 -m venv ../venv
source ../venv/bin/activate   # Linux/macOS
# ..\venv\Scripts\activate    # Windows
```

### 2. Install Python dependencies

```bash
pip install django djangorestframework psycopg2-binary django-redis \
            requests django-cors-headers celery redis drf-yasg
```

### 3. Configure environment variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `backend/.env` and set your News API key (get from https://newsapi.org/):

```env
NEWS_API_KEY=your_actual_newsapi_key_here
DB_NAME=lamia_news
DB_USER=lamia_user
DB_PASSWORD=lamia_pass123
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

**Note:** The `.env` file is already in `.gitignore` and will not be committed to version control.

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Fetch initial news data

```bash
# Fetch all categories
python manage.py fetch_news --all-categories

# Or fetch a specific category
python manage.py fetch_news --category technology

# Or search by keyword
python manage.py fetch_news --query "artificial intelligence"
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

---

## Frontend Setup (Angular)

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start the development server

```bash
ng serve
```

The app will be available at `http://localhost:4200/`.

---

## Database & Caching Setup

### PostgreSQL Setup

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Start the service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql -c "CREATE USER lamia_user WITH PASSWORD 'lamia_pass123';"
sudo -u postgres psql -c "CREATE DATABASE lamia_news OWNER lamia_user;"
sudo -u postgres psql -c "ALTER USER lamia_user CREATEDB;"
```

### Redis Setup

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start the service
sudo systemctl start redis-server

# Verify it's running
redis-cli ping   # Should return PONG
```

### Celery Worker (for periodic news fetching)

```bash
# In a separate terminal, start the Celery worker
cd backend
source ../venv/bin/activate
celery -A backend worker --loglevel=info

# In another terminal, start Celery Beat (scheduler)
celery -A backend beat --loglevel=info
```

Celery Beat is configured to fetch news every **30 minutes** automatically.

---

## API Documentation

### Interactive Documentation

| URL                              | Description         |
| -------------------------------- | ------------------- |
| `http://localhost:8000/swagger/` | Swagger UI          |
| `http://localhost:8000/redoc/`   | ReDoc documentation |
| `http://localhost:8000/admin/`   | Django Admin panel  |

### Endpoints

#### Articles

| Method | Endpoint                   | Description                        |
| ------ | -------------------------- | ---------------------------------- |
| GET    | `/api/news/articles/`      | List articles (paginated, 50/page) |
| GET    | `/api/news/articles/<id>/` | Get article details                |
| POST   | `/api/news/fetch/`         | Manually trigger news fetch        |

**Query Parameters for `/api/news/articles/`:**

| Parameter  | Type   | Description                                 |
| ---------- | ------ | ------------------------------------------- |
| `page`     | int    | Page number (default: 1)                    |
| `category` | string | Filter by category slug (e.g. `technology`) |
| `source`   | string | Filter by source ID (e.g. `bbc-news`)       |
| `country`  | string | Filter by country code (e.g. `us`)          |
| `search`   | string | Full-text search on title & description     |

**Example requests:**

```bash
# Get all articles (page 1)
curl http://localhost:8000/api/news/articles/

# Filter by category
curl http://localhost:8000/api/news/articles/?category=technology

# Search articles
curl http://localhost:8000/api/news/articles/?search=AI

# Combine filters
curl "http://localhost:8000/api/news/articles/?category=technology&search=AI&page=2"
```

#### Categories

| Method | Endpoint                | Description                       |
| ------ | ----------------------- | --------------------------------- |
| GET    | `/api/news/categories/` | List all categories (with counts) |

#### Sources

| Method | Endpoint             | Description                    |
| ------ | -------------------- | ------------------------------ |
| GET    | `/api/news/sources/` | List all sources (with counts) |

#### Fetch Trigger

| Method | Endpoint           | Description               |
| ------ | ------------------ | ------------------------- |
| POST   | `/api/news/fetch/` | Trigger manual news fetch |

**POST body:**

```json
{
  "category": "technology",
  "country": "us",
  "query": "AI"
}
```

---

## Database Optimization

### 1. Indexing Strategy

The application uses several index types to optimize queries:

| Index Type    | Fields                         | Purpose                             |
| ------------- | ------------------------------ | ----------------------------------- |
| B-tree        | `published_at DESC`            | Fast default ordering               |
| Composite     | `(category, -published_at)`    | Category filter + date ordering     |
| Composite     | `(source_name, -published_at)` | Source filter + date ordering       |
| Composite     | `(country, -published_at)`     | Country filter + date ordering      |
| GIN (trigram) | `title`                        | Fast `ICONTAINS` / full-text search |
| GIN (trigram) | `description`                  | Fast `ICONTAINS` / full-text search |
| Unique        | `url`                          | Deduplication during upsert         |

### 2. Table Partitioning

The database uses a **partitioned archive table** (`news_article_archive`) for old articles:

- Partitioned by `published_at` using **range partitioning** (quarterly).
- Articles older than 90 days can be archived using the `archive_old_articles()` PostgreSQL function.
- This keeps the main `news_article` table lean for fast queries.

```sql
-- Archive old articles (run periodically)
SELECT archive_old_articles();
```

### 3. Caching Strategy

| Cache Target           | TTL     | Purpose                              |
| ---------------------- | ------- | ------------------------------------ |
| Article list responses | 10 min  | Reduce DB load for paginated queries |
| Category list          | 15 min  | Categories rarely change             |
| Source list            | 15 min  | Sources rarely change                |
| Django sessions        | Default | Session data stored in Redis         |

**Cache backend:** Redis with `django-redis`, pickle serialization, and zlib compression.

**Performance optimizations:**

- `defer()` excludes heavy `content` field from list queries
- `only()` limits SELECT fields to minimize data transfer
- Redis connection pool: 100 connections with retry on timeout
- Compressed cache storage with zlib
- Cache warmup command: `python manage.py warmup_cache`

### 4. Query Optimization

- `select_related("category", "source")` on article queries to avoid N+1 queries.
- Lightweight `ArticleListSerializer` for list views (omits `content` field).
- `CONN_MAX_AGE=600` for persistent database connections.
- `statement_timeout=30s` to prevent long-running queries.

---

## Project Structure

```
lamia/
├── backend/                    # Django REST API
│   ├── backend/                # Project configuration
│   │   ├── settings.py         # Django settings (DB, cache, CORS, Celery)
│   │   ├── urls.py             # Root URL configuration
│   │   ├── celery.py           # Celery app configuration
│   │   └── wsgi.py             # WSGI entry point
│   ├── news/                   # News application
│   │   ├── models.py           # Article, Category, Source models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # API views with caching
│   │   ├── urls.py             # News app URL patterns
│   │   ├── services.py         # News API service layer
│   │   ├── tasks.py            # Celery periodic tasks
│   │   ├── admin.py            # Django admin configuration
│   │   ├── tests.py            # Unit tests
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── fetch_news.py  # CLI command to fetch news
│   │   └── migrations/
│   │       ├── 0001_initial.py
│   │       └── 0002_database_optimization.py  # GIN indexes & partitioning
│   └── manage.py
├── frontend/                   # Angular application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── header/            # App header
│   │   │   │   ├── dashboard/         # Main dashboard with filters
│   │   │   │   └── article-card/      # Article card component
│   │   │   ├── models/
│   │   │   │   └── news.model.ts      # TypeScript interfaces
│   │   │   ├── services/
│   │   │   │   └── news.service.ts    # HTTP service
│   │   │   ├── app.ts                 # Root component
│   │   │   ├── app.routes.ts          # Routing
│   │   │   └── app.config.ts          # App configuration
│   │   └── styles.css                 # Global styles (Tailwind)
│   ├── angular.json
│   └── package.json
├── venv/                       # Python virtual environment
└── README.md                   # This file
```

---

## Quick Start (All-in-One)

```bash
# 1. Start PostgreSQL & Redis
sudo systemctl start postgresql redis-server

# 2. Backend
cd backend
source ../venv/bin/activate
export NEWS_API_KEY=your_key_here
python manage.py migrate
python manage.py fetch_news --all-categories
python manage.py runserver &

# 3. Frontend (new terminal)
cd frontend
npm install
ng serve
```

Open `http://localhost:4200` in your browser.
