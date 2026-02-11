# 📰 Latest News Dashboard

A production-grade full-stack news aggregation platform that fetches, stores, caches, and displays articles from [NewsAPI](https://newsapi.org/).

---

## 1. System Overview

The application provides:

* Periodic news ingestion from NewsAPI
* Deduplicated storage in PostgreSQL
* RESTful APIs with filtering, search, and pagination
* Redis-backed caching
* Asynchronous background processing via Celery
* Interactive API documentation (Swagger & ReDoc)
* Angular-based responsive frontend

---

## 2. Architecture

```
Angular (localhost:4200)
        │
        ▼
Django REST API (localhost:8000)
        │
        ├── PostgreSQL (Primary Database)
        ├── Redis (Cache Layer)
        └── Redis (Celery Broker)
                │
                ▼
        Celery Worker + Celery Beat
```

### Architectural Responsibilities

| Component   | Responsibility                 |
| ----------- | ------------------------------ |
| Angular     | UI rendering & API consumption |
| Django REST | API layer, business logic      |
| PostgreSQL  | Persistent storage             |
| Redis       | Caching + task broker          |
| Celery      | Background task processing     |

---

## 3. Technology Stack

| Layer            | Technology                     |
| ---------------- | ------------------------------ |
| Frontend         | Angular                        |
| Backend          | Django + Django REST Framework |
| Database         | PostgreSQL                     |
| Caching          | Redis                          |
| Async Processing | Celery + Celery Beat           |
| API Docs         | drf-yasg (Swagger)             |

---

## 4. Prerequisites

| Tool        | Version |
| ----------- | ------- |
| Python      | 3.10+   |
| Node.js     | 18+     |
| PostgreSQL  | 14+     |
| Redis       | 7+      |
| Angular CLI | 19+     |

---

## 5. Installation

### 5.1 Clone Repository

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_ROOT>
```

---

### 5.2 Database Setup (PostgreSQL)

```sql
CREATE USER news_user WITH PASSWORD 'secure_password';
CREATE DATABASE news_dashboard OWNER news_user;
```

---

### 5.3 Redis Setup

Linux/macOS:

```bash
sudo apt install redis-server
sudo systemctl start redis
redis-cli ping
```

Expected output:

```
PONG
```

Windows: Use WSL.

---

## 6. Backend Setup (Django)

### 6.1 Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

---

### 6.2 Install Dependencies

```bash
pip install -r requirements.txt
```

If missing:

```bash
pip install django djangorestframework psycopg2-binary django-redis requests django-cors-headers celery redis drf-yasg python-dotenv
```

---

### 6.3 Environment Configuration

Create `backend/.env`:

```env
NEWS_API_KEY=your_newsapi_key_here

DB_NAME=news_dashboard
DB_USER=news_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

Ensure:

* `.env` is excluded from version control
* `.env.example` is provided

---

### 6.4 Apply Migrations

```bash
cd backend
python manage.py migrate
```

---

### 6.5 Initial Data Fetch

```bash
python manage.py fetch_news --all-categories
```

---

### 6.6 Start Backend

```bash
python manage.py runserver
```

API base URL:

```
http://127.0.0.1:8000
```

---

## 7. Frontend Setup (Angular)

```bash
cd frontend
npm install
npx ng serve
```

Frontend:

```
http://localhost:4200
```

---

## 8. Running the System

Start in the following order:

1. Redis
2. Django backend
3. Celery worker
4. Celery beat
5. Angular frontend

---

## 9. Background Tasks (Celery)

Worker:

```bash
celery -A backend worker --loglevel=info
```

Scheduler:

```bash
celery -A backend beat --loglevel=info
```

Celery Beat automatically triggers periodic news ingestion.

---

## 10. API Documentation

| Tool    | URL                                                              |
| ------- | ---------------------------------------------------------------- |
| Swagger | [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) |
| ReDoc   | [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)     |

---

## 11. API Endpoints

### Articles

```
GET /api/news/articles/
```

Query parameters:

* `page`
* `category`
* `source`
* `country`
* `search`

Example:

```bash
curl "http://127.0.0.1:8000/api/news/articles/?search=AI"
```

---

### Categories

```
GET /api/news/categories/
```

---

### Sources

```
GET /api/news/sources/
```

---

### Manual Fetch

```
POST /api/news/fetch/
```

Example body:

```json
{
  "category": "technology",
  "country": "us",
  "query": "AI"
}
```

---

## 12. Database Design & Optimization

### Indexing Strategy

* B-tree index on `published_at`
* Composite index `(category, published_at)`
* Composite index `(source, published_at)`
* GIN trigram index for full-text search
* Unique constraint on `url`

### Partitioning Strategy

Range partitioning for archival of historical articles.

---

## 13. Caching Strategy

| Resource   | TTL        |
| ---------- | ---------- |
| Articles   | 10 minutes |
| Categories | 15 minutes |
| Sources    | 15 minutes |

Clear cache:

```bash
python manage.py shell
```

```python
from django.core.cache import cache
cache.clear()
exit()
```

---

## 14. Project Structure

```
backend/
│
├── backend/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
│
├── news/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── services.py
│   └── tasks.py
│
└── manage.py

frontend/
└── src/app/
    ├── components/
    └── services/
```

---

## 15. Troubleshooting

### Backend Unreachable

```bash
python manage.py runserver
curl http://127.0.0.1:8000/api/news/articles/
```

---

### Angular Not Recognized

```bash
npx ng serve
```

---

### Articles Not Updating

* Verify Celery worker is running
* Verify Redis is active
* Clear cache

---

## 16. Submission Checklist

* `.env` excluded from version control
* `.env.example` included
* README complete and reproducible
* Swagger accessible
* Application runs end-to-end
* Code structured and documented

---

## Author

**Lamia Ben Salem**
