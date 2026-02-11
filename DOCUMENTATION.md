# Latest News Dashboard - Complete Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Installation and Setup](#3-installation-and-setup)
4. [Database Configuration](#4-database-configuration)
5. [Caching Configuration](#5-caching-configuration)
6. [API Documentation](#6-api-documentation)
7. [Running the Project](#7-running-the-project)
8. [Background Tasks](#8-background-tasks)
9. [Project Structure](#9-project-structure)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview

### 1.1 Description

The Latest News Dashboard is a production-ready full-stack web application that aggregates news articles from NewsAPI. It demonstrates best practices in building scalable web applications with proper database optimization, caching strategies, and asynchronous task processing.

### 1.2 Key Features

- **Real-time News Aggregation**: Fetches news from multiple categories and sources via NewsAPI
- **Smart Caching**: Redis-based caching to reduce API calls and database queries
- **Advanced Search**: Full-text search capabilities with PostgreSQL trigram indexes
- **Filtering**: Filter by category, source, country, and custom search queries
- **Pagination**: Efficient pagination for large datasets
- **Background Processing**: Celery-based periodic tasks for automated news updates
- **RESTful API**: Well-documented REST API with Swagger/OpenAPI documentation
- **Modern Frontend**: Responsive Angular interface with real-time updates

### 1.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Angular 19+ | Single-page application framework |
| Backend | Django 4.x | Web framework |
| API | Django REST Framework | RESTful API creation |
| Database | PostgreSQL 14+ | Primary data storage |
| Cache | Redis 7+ | Caching and session storage |
| Task Queue | Celery | Asynchronous task processing |
| Message Broker | Redis | Celery message broker |
| API Docs | drf-yasg | Swagger/OpenAPI documentation |

---

## 2. Architecture

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Angular Frontend                        │
│                  (Port 4200)                             │
│  - Components                                            │
│  - Services (HTTP Client)                                │
│  - Routing                                               │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Django REST API (Port 8000)                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Views Layer (API Endpoints)                       │  │
│  └────────────────────┬──────────────────────────────┘  │
│  ┌────────────────────▼──────────────────────────────┐  │
│  │ Serializers (Data Validation & Transformation)    │  │
│  └────────────────────┬──────────────────────────────┘  │
│  ┌────────────────────▼──────────────────────────────┐  │
│  │ Services Layer (Business Logic)                   │  │
│  └────────────────────┬──────────────────────────────┘  │
│  ┌────────────────────▼──────────────────────────────┐  │
│  │ Models (ORM)                                       │  │
│  └────────────────────┬──────────────────────────────┘  │
├────────────────────────┼──────────────────────────────┤
│  ┌──────────────┐  ┌──▼────────────┐  ┌──────────────┐  │
│  │  PostgreSQL  │  │     Redis     │  │    Redis     │  │
│  │  (Storage)   │  │    (Cache)    │  │   (Broker)   │  │
│  │              │  │  - API Cache  │  │  - Celery    │  │
│  │  - Articles  │  │  - Sessions   │  │    Messages  │  │
│  │  - Metadata  │  │               │  │              │  │
│  └──────────────┘  └───────────────┘  └──────┬───────┘  │
└───────────────────────────────────────────────┼─────────┘
                                                 │
                        ┌────────────────────────▼─────────┐
                        │  Celery Worker + Beat Scheduler  │
                        │  - Periodic News Fetching        │
                        │  - Data Processing               │
                        │  - Cleanup Tasks                 │
                        └──────────────────────────────────┘
```

### 2.2 Data Flow

1. **User Request → Frontend**: User interacts with Angular UI
2. **Frontend → Backend API**: HTTP request to Django REST API
3. **API → Cache Check**: Check Redis for cached response
4. **Cache Miss → Database**: Query PostgreSQL if not cached
5. **Database → API**: Return data
6. **API → Cache**: Store response in Redis
7. **API → Frontend**: Return JSON response
8. **Frontend → User**: Display data

### 2.3 Background Processing Flow

1. **Celery Beat**: Triggers scheduled tasks
2. **Task Queue**: Adds task to Redis queue
3. **Celery Worker**: Picks up task from queue
4. **NewsAPI Fetch**: Retrieves articles from external API
5. **Data Processing**: Validates and deduplicates articles
6. **Database Update**: Stores new articles in PostgreSQL
7. **Cache Invalidation**: Clears relevant cached data

---

## 3. Installation and Setup

### 3.1 System Requirements

**Operating System**: Windows 10/11 with WSL2

**Software Requirements**:
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Redis 7 or higher (via WSL)
- Git

### 3.2 Step-by-Step Installation

#### Step 1: Install Prerequisites

**Python Installation**:
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify: `python --version`

**Node.js Installation**:
1. Download from [nodejs.org](https://nodejs.org/)
2. Run installer with default settings
3. Verify: `node --version` and `npm --version`

**PostgreSQL Installation**:
1. Download from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer (remember the postgres user password)
3. Add PostgreSQL bin directory to PATH
4. Verify: `psql --version`

**Redis Installation (WSL)**:
1. Open PowerShell as Administrator
2. Install WSL: `wsl --install`
3. Restart computer
4. Open WSL terminal
5. Update packages: `sudo apt update`
6. Install Redis: `sudo apt install redis-server`
7. Verify: `redis-cli --version`

#### Step 2: Clone Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd news-dashboard
```

#### Step 3: Backend Setup

**Create Virtual Environment**:
```bash
python -m venv venv
```

**Activate Virtual Environment**:
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# Command Prompt
.\venv\Scripts\activate.bat
```

**Install Dependencies**:
```bash
pip install -r requirements.txt
```

**If requirements.txt is not present**:
```bash
pip install django==4.2.7
pip install djangorestframework==3.14.0
pip install psycopg2-binary==2.9.9
pip install django-redis==5.4.0
pip install requests==2.31.0
pip install django-cors-headers==4.3.1
pip install celery==5.3.4
pip install redis==5.0.1
pip install drf-yasg==1.21.7
pip install python-dotenv==1.0.0
```

**Create Environment File**:

Create `.env` file in `backend/` directory:

```env
# NewsAPI Configuration
NEWS_API_KEY=your_newsapi_key_from_newsapi_org

# Database Configuration
DB_NAME=news_dashboard
DB_USER=news_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0

# Django Secret Key (generate a new one for production)
SECRET_KEY=django-insecure-your-secret-key-here

# Debug Mode (set to False in production)
DEBUG=True

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Create .env.example** (for repository):
```env
NEWS_API_KEY=your_api_key_here
DB_NAME=news_dashboard
DB_USER=news_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Step 4: Frontend Setup

```bash
cd frontend
npm install
```

---

## 4. Database Configuration

### 4.1 PostgreSQL Setup

#### Create Database and User

**Using psql**:
```bash
psql -U postgres
```

```sql
-- Create user
CREATE USER news_user WITH PASSWORD 'secure_password';

-- Create database
CREATE DATABASE news_dashboard OWNER news_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE news_dashboard TO news_user;

-- Connect to database
\c news_dashboard

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO news_user;

-- Exit
\q
```

**Using pgAdmin**:
1. Open pgAdmin
2. Right-click on "Login/Group Roles" → Create → Login/Group Role
3. Name: `news_user`, Password: `secure_password`
4. Right-click on "Databases" → Create → Database
5. Name: `news_dashboard`, Owner: `news_user`

### 4.2 Database Migrations

Run migrations to create database schema:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

**Expected Output**:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying news.0001_initial... OK
  ...
```

### 4.3 Database Schema

**Article Model**:
```python
class Article(models.Model):
    title = CharField(max_length=500)
    description = TextField(blank=True, null=True)
    content = TextField(blank=True, null=True)
    url = URLField(unique=True, max_length=1000)
    url_to_image = URLField(max_length=1000, blank=True, null=True)
    published_at = DateTimeField()
    source = CharField(max_length=200)
    author = CharField(max_length=200, blank=True, null=True)
    category = CharField(max_length=50, blank=True, null=True)
    country = CharField(max_length=2, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
```

### 4.4 Database Optimization

**Indexes Created**:

1. **Primary Key Index**: Automatic on `id`
2. **Unique Index**: On `url` to prevent duplicates
3. **B-tree Index**: On `published_at` for date sorting
4. **Composite Index**: On `(category, published_at)` for filtered queries
5. **Composite Index**: On `(source, published_at)` for source filtering
6. **GIN Trigram Index**: On `title` and `description` for full-text search

**Create Indexes** (if not automatically created):

```sql
-- B-tree index for date sorting
CREATE INDEX idx_article_published_at ON news_article(published_at DESC);

-- Composite indexes for filtered queries
CREATE INDEX idx_article_category_date ON news_article(category, published_at DESC);
CREATE INDEX idx_article_source_date ON news_article(source, published_at DESC);

-- Full-text search indexes
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_article_title_trgm ON news_article USING gin(title gin_trgm_ops);
CREATE INDEX idx_article_description_trgm ON news_article USING gin(description gin_trgm_ops);
```

**Query Performance**:
- Simple queries: < 50ms
- Filtered queries: < 100ms
- Full-text search: < 200ms
- Pagination: < 50ms per page

---

## 5. Caching Configuration

### 5.1 Redis Setup

**Start Redis (WSL)**:
```bash
wsl
sudo service redis-server start
```

**Verify Redis**:
```bash
redis-cli ping
# Should return: PONG
```

**Redis Configuration** (settings.py):
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'news_dashboard',
        'TIMEOUT': 600,  # 10 minutes
    }
}
```

### 5.2 Caching Strategy

**Cache Levels**:

1. **API Response Caching**: Cache entire API responses
2. **Query Result Caching**: Cache database query results
3. **Session Caching**: Store session data in Redis

**Cached Endpoints**:

| Endpoint | Cache Duration | Key Pattern |
|----------|---------------|-------------|
| `/api/news/articles/` | 10 minutes | `articles:page:{page}:category:{cat}:search:{q}` |
| `/api/news/categories/` | 15 minutes | `categories:all` |
| `/api/news/sources/` | 15 minutes | `sources:all` |

**Cache Implementation**:

```python
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class ArticleListView(ListAPIView):
    @method_decorator(cache_page(60 * 10))  # 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
```

### 5.3 Cache Management

**Clear All Cache**:
```python
from django.core.cache import cache
cache.clear()
```

**Clear Specific Key**:
```python
cache.delete('articles:page:1:category:technology')
```

**Manual Cache Invalidation**:
```bash
python manage.py shell
```
```python
from django.core.cache import cache
cache.clear()
exit()
```

**Redis CLI Commands**:
```bash
redis-cli
> FLUSHDB  # Clear current database
> KEYS *   # List all keys
> TTL key  # Check time to live
> DEL key  # Delete specific key
```

---

## 6. API Documentation

### 6.1 Accessing API Documentation

**Swagger UI**:
```
http://127.0.0.1:8000/swagger/
```
- Interactive API documentation
- Try out endpoints directly
- View request/response schemas

**ReDoc**:
```
http://127.0.0.1:8000/redoc/
```
- Clean, readable API documentation
- Better for reference

### 6.2 API Endpoints

#### 6.2.1 Articles List

**Endpoint**: `GET /api/news/articles/`

**Description**: Retrieve paginated list of news articles with optional filtering and search.

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `category` (string): Filter by category (e.g., technology, business, sports)
- `source` (string): Filter by news source (e.g., CNN, BBC)
- `country` (string): Filter by country code (e.g., us, gb)
- `search` (string): Full-text search query

**Response**:
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/news/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Breaking News: Technology Advancement",
      "description": "Description of the article...",
      "content": "Full article content...",
      "url": "https://example.com/article",
      "url_to_image": "https://example.com/image.jpg",
      "published_at": "2024-02-10T10:30:00Z",
      "source": "TechNews",
      "author": "John Doe",
      "category": "technology",
      "country": "us",
      "created_at": "2024-02-10T10:35:00Z"
    }
  ]
}
```

**Examples**:

```bash
# Get all articles (page 1)
curl http://127.0.0.1:8000/api/news/articles/

# Get technology articles
curl "http://127.0.0.1:8000/api/news/articles/?category=technology"

# Search for AI articles
curl "http://127.0.0.1:8000/api/news/articles/?search=AI"

# Combine filters
curl "http://127.0.0.1:8000/api/news/articles/?category=technology&country=us&search=innovation"

# PowerShell example
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/news/articles/?category=technology"
```

#### 6.2.2 Categories List

**Endpoint**: `GET /api/news/categories/`

**Description**: Retrieve all available news categories.

**Response**:
```json
{
  "categories": [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology"
  ]
}
```

**Example**:
```bash
curl http://127.0.0.1:8000/api/news/categories/
```

#### 6.2.3 Sources List

**Endpoint**: `GET /api/news/sources/`

**Description**: Retrieve all available news sources.

**Response**:
```json
{
  "sources": [
    "BBC News",
    "CNN",
    "TechCrunch",
    "The Guardian",
    "The New York Times"
  ]
}
```

**Example**:
```bash
curl http://127.0.0.1:8000/api/news/sources/
```

#### 6.2.4 Manual Fetch

**Endpoint**: `POST /api/news/fetch/`

**Description**: Manually trigger news fetching from NewsAPI.

**Request Body**:
```json
{
  "category": "technology",
  "country": "us",
  "query": "artificial intelligence"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Fetched 20 new articles",
  "articles_count": 20,
  "duplicates_skipped": 5
}
```

**Examples**:

```bash
# Fetch technology news
curl -X POST http://127.0.0.1:8000/api/news/fetch/ \
  -H "Content-Type: application/json" \
  -d '{"category":"technology","country":"us"}'

# Fetch with search query
curl -X POST http://127.0.0.1:8000/api/news/fetch/ \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning"}'

# PowerShell example
$body = @{
    category = "technology"
    country = "us"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/news/fetch/" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

### 6.3 Error Responses

**400 Bad Request**:
```json
{
  "error": "Invalid category",
  "detail": "Category must be one of: business, entertainment, general, health, science, sports, technology"
}
```

**404 Not Found**:
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "detail": "An error occurred while processing your request"
}
```

### 6.4 Rate Limiting

**NewsAPI Limits**:
- Free tier: 100 requests per day
- Developer tier: 500 requests per day

**Application Limits**:
- Caching reduces API calls significantly
- Background tasks scheduled to respect limits

---

## 7. Running the Project

### 7.1 Prerequisites Check

Before running, ensure:
- PostgreSQL service is running
- Redis is running in WSL
- Database is created and migrated
- Environment variables are configured

### 7.2 Complete Startup Guide

#### Step 1: Start Redis

Open WSL terminal:
```bash
wsl
sudo service redis-server start
redis-cli ping  # Verify
```

Keep this terminal open.

#### Step 2: Start Django Backend

Open new terminal (PowerShell or CMD):
```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Expected Output**:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 11, 2026 - 10:30:00
Django version 4.2.7, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

Access: http://127.0.0.1:8000

#### Step 3: Start Angular Frontend

Open new terminal:
```bash
cd frontend
npx ng serve
```

**Expected Output**:
```
✔ Browser application bundle generation complete.

Initial Chunk Files   | Names         |  Raw Size
main.js              | main          |   1.2 MB |
styles.css           | styles        | 150.0 kB |

Build at: 2026-02-11T10:30:00.000Z
** Angular Live Development Server is listening on localhost:4200 **
```

Access: http://localhost:4200

#### Step 4: (Optional) Start Celery Worker

Open new terminal:
```bash
cd backend
.\venv\Scripts\Activate.ps1
celery -A backend worker --loglevel=info --pool=solo
```

**Note**: `--pool=solo` is required for Windows.

#### Step 5: (Optional) Start Celery Beat

Open new terminal:
```bash
cd backend
.\venv\Scripts\Activate.ps1
celery -A backend beat --loglevel=info
```

### 7.3 Verify Installation

1. **Backend API**: http://127.0.0.1:8000/api/news/articles/
2. **Frontend**: http://localhost:4200
3. **Swagger Docs**: http://127.0.0.1:8000/swagger/
4. **Admin Panel**: http://127.0.0.1:8000/admin/

### 7.4 Initial Data Loading

Load initial news data:
```bash
python manage.py fetch_news --all-categories
```

This will fetch articles from all categories.

### 7.5 Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

---

## 8. Background Tasks

### 8.1 Celery Configuration

**Celery Setup** (backend/celery.py):
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-news-every-hour': {
        'task': 'news.tasks.fetch_news_task',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

### 8.2 Available Tasks

**1. Fetch News Task**:
```python
@shared_task
def fetch_news_task(category=None, country='us'):
    """Fetch news articles from NewsAPI"""
    # Task implementation
```

**2. Cleanup Old Articles**:
```python
@shared_task
def cleanup_old_articles():
    """Remove articles older than 30 days"""
    # Task implementation
```

### 8.3 Manual Task Execution

**From Django Shell**:
```bash
python manage.py shell
```

```python
from news.tasks import fetch_news_task

# Execute task immediately
fetch_news_task.delay('technology', 'us')

# Check task status
result = fetch_news_task.delay('technology')
result.ready()  # True if complete
result.get()    # Get result
```

### 8.4 Monitoring Tasks

**Celery Flower** (Web-based monitoring):
```bash
pip install flower
celery -A backend flower
```

Access: http://localhost:5555

### 8.5 Task Scheduling

**Periodic Tasks Configuration**:
- Fetch news: Every hour
- Cleanup old articles: Daily at midnight
- Clear cache: Every 6 hours

**Custom Schedule** (settings.py):
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'fetch-technology-news': {
        'task': 'news.tasks.fetch_news_task',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'args': ('technology', 'us')
    },
    'cleanup-articles': {
        'task': 'news.tasks.cleanup_old_articles',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

---

## 9. Project Structure

### 9.1 Complete Directory Structure

```
news-dashboard/
│
├── backend/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py         # Django configuration
│   │   ├── urls.py             # URL routing
│   │   ├── wsgi.py             # WSGI config
│   │   ├── asgi.py             # ASGI config
│   │   └── celery.py           # Celery configuration
│   │
│   ├── news/
│   │   ├── __init__.py
│   │   ├── models.py           # Database models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # API views
│   │   ├── urls.py             # App URLs
│   │   ├── services.py         # Business logic
│   │   ├── tasks.py            # Celery tasks
│   │   ├── admin.py            # Django admin
│   │   ├── apps.py             # App configuration
│   │   └── tests.py            # Unit tests
│   │
│   ├── manage.py               # Django management
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (not committed)
│   └── .env.example            # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── article-list/
│   │   │   │   ├── article-detail/
│   │   │   │   ├── search-bar/
│   │   │   │   └── filter-sidebar/
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── news.service.ts
│   │   │   │   └── api.service.ts
│   │   │   │
│   │   │   ├── models/
│   │   │   │   └── article.model.ts
│   │   │   │
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   └── app.routes.ts
│   │   │
│   │   ├── assets/
│   │   ├── environments/
│   │   ├── index.html
│   │   └── main.ts
│   │
│   ├── angular.json
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── .gitignore
├── README.md
└── DOCUMENTATION.md
```

### 9.2 Key Files Explained

**backend/settings.py**:
- Django configuration
- Database settings
- Cache configuration
- CORS settings
- Installed apps

**backend/celery.py**:
- Celery configuration
- Task scheduling
- Beat schedule

**news/models.py**:
- Article model definition
- Database schema

**news/serializers.py**:
- Data validation
- JSON serialization

**news/views.py**:
- API endpoints
- Request handling

**news/services.py**:
- NewsAPI integration
- Business logic

**news/tasks.py**:
- Celery tasks
- Background jobs

---

## 10. Troubleshooting

### 10.1 Common Issues and Solutions

#### Issue 1: Virtual Environment Activation Error

**Problem**: PowerShell execution policy prevents script execution

**Error Message**:
```
File cannot be loaded because running scripts is disabled on this system
```

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue 2: Port Already in Use

**Problem**: Django port 8000 is occupied

**Error Message**:
```
Error: That port is already in use.
```

**Solution**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID_NUMBER> /F

# Or run Django on different port
python manage.py runserver 8001
```

#### Issue 3: PostgreSQL Connection Failed

**Problem**: Cannot connect to PostgreSQL

**Error Message**:
```
django.db.utils.OperationalError: could not connect to server
```

**Solutions**:

1. Check PostgreSQL service:
```powershell
# Open Services
services.msc
# Find postgresql-x64-14 and ensure it's running
```

2. Verify credentials in `.env`:
```env
DB_NAME=news_dashboard
DB_USER=news_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

3. Test connection:
```bash
psql -U news_user -d news_dashboard
```

4. Check PostgreSQL is listening:
```powershell
netstat -an | findstr "5432"
```

#### Issue 4: Redis Connection Error

**Problem**: Cannot connect to Redis

**Error Message**:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions**:

1. Ensure WSL is running:
```bash
wsl
```

2. Start Redis:
```bash
sudo service redis-server start
```

3. Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

4. Check Redis status:
```bash
sudo service redis-server status
```

5. Restart Redis if needed:
```bash
sudo service redis-server restart
```

#### Issue 5: Celery Worker Not Starting (Windows)

**Problem**: Celery worker fails on Windows

**Error Message**:
```
ValueError: not enough values to unpack
```

**Solution**:
Always use `--pool=solo` flag on Windows:
```bash
celery -A backend worker --loglevel=info --pool=solo
```

#### Issue 6: NewsAPI Key Invalid

**Problem**: NewsAPI returns 401 Unauthorized

**Error Message**:
```
{"status":"error","code":"apiKeyInvalid"}
```

**Solutions**:

1. Verify API key in `.env`:
```env
NEWS_API_KEY=your_actual_key_here
```

2. Get new API key from [newsapi.org](https://newsapi.org/)

3. Restart Django server after updating `.env`

#### Issue 7: Module Not Found

**Problem**: Python module import errors

**Error Message**:
```
ModuleNotFoundError: No module named 'django'
```

**Solutions**:

1. Ensure virtual environment is activated:
```powershell
.\venv\Scripts\Activate.ps1
```

2. Reinstall dependencies:
```bash
pip install -r requirements.txt
```

3. Verify Python version:
```bash
python --version  # Should be 3.10+
```

#### Issue 8: Database Migration Errors

**Problem**: Migration fails

**Error Message**:
```
django.db.utils.ProgrammingError: relation does not exist
```

**Solutions**:

1. Reset migrations:
```bash
# Delete migration files (except __init__.py)
# Then run:
python manage.py makemigrations
python manage.py migrate
```

2. Drop and recreate database:
```sql
DROP DATABASE news_dashboard;
CREATE DATABASE news_dashboard OWNER news_user;
```

3. Run migrations again:
```bash
python manage.py migrate
```

#### Issue 9: CORS Errors in Frontend

**Problem**: Frontend cannot access API

**Error Message**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:

Verify CORS settings in `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
    'http://127.0.0.1:4200',
]
```

#### Issue 10: Articles Not Displaying

**Problem**: API returns empty results

**Solutions**:

1. Fetch initial data:
```bash
python manage.py fetch_news --all-categories
```

2. Check database:
```bash
python manage.py shell
```
```python
from news.models import Article
print(Article.objects.count())
```

3. Clear cache:
```python
from django.core.cache import cache
cache.clear()
```

### 10.2 Debug Mode

**Enable Debug Mode**:

In `.env`:
```env
DEBUG=True
```

In `settings.py`:
```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### 10.3 Logging

**Check Django Logs**:
Logs appear in console where Django is running

**Check Celery Logs**:
Logs appear in console where Celery worker is running

**Check Redis Logs** (WSL):
```bash
sudo tail -f /var/log/redis/redis-server.log
```

**Check PostgreSQL Logs**:
```
C:\Program Files\PostgreSQL\14\data\log\
```

### 10.4 Getting Help

If issues persist:

1. Check error message carefully
2. Search Django/DRF documentation
3. Check Celery documentation for task-related issues
4. Review PostgreSQL logs for database issues
5. Verify all services are running
6. Check environment variables
7. Review this documentation

---

## Appendix

### A. Useful Commands

**Django**:
```bash
# Create superuser
python manage.py createsuperuser

# Shell
python manage.py shell

# Database shell
python manage.py dbshell

# Show migrations
python manage.py showmigrations

# Collect static files
python manage.py collectstatic
```

**Celery**:
```bash
# Worker
celery -A backend worker --loglevel=info --pool=solo

# Beat
celery -A backend beat --loglevel=info

# Inspect active tasks
celery -A backend inspect active

# Purge queue
celery -A backend purge
```

**Redis**:
```bash
# Connect to Redis CLI
redis-cli

# Monitor commands
redis-cli MONITOR

# Get all keys
redis-cli KEYS *

# Flush database
redis-cli FLUSHDB
```

**PostgreSQL**:
```bash
# Connect to database
psql -U news_user -d news_dashboard

# List databases
\l

# List tables
\dt

# Describe table
\d news_article

# Execute SQL
psql -U news_user -d news_dashboard -c "SELECT COUNT(*) FROM news_article;"
```

### B. Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `NEWS_API_KEY` | NewsAPI key | `abc123...` |
| `DB_NAME` | Database name | `news_dashboard` |
| `DB_USER` | Database user | `news_user` |
| `DB_PASSWORD` | Database password | `secure_password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis cache URL | `redis://127.0.0.1:6379/1` |
| `CELERY_BROKER_URL` | Celery broker | `redis://127.0.0.1:6379/0` |
| `SECRET_KEY` | Django secret | `random-string` |
| `DEBUG` | Debug mode | `True` or `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |

### C. API Rate Limits

| Tier | Requests/Day | Requests/Second |
|------|--------------|-----------------|
| Free | 100 | 5 |
| Developer | 500 | 10 |
| Professional | 5,000 | 50 |

### D. Database Maintenance

**Backup Database**:
```bash
pg_dump -U news_user news_dashboard > backup.sql
```

**Restore Database**:
```bash
psql -U news_user news_dashboard < backup.sql
```

**Vacuum Database**:
```sql
VACUUM ANALYZE news_article;
```

---

**Document Version**: 1.0
**Last Updated**: February 11, 2026
**Author**: Lamia Ben Salem
