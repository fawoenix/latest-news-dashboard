# Latest News Dashboard

A full-stack web application that fetches and displays news from the [News API](https://newsapi.org/), built with **Django REST Framework** (backend), **Angular** (frontend), **PostgreSQL** (database), and **Redis** (caching).

For full documentation including detailed API reference, database design, and caching strategy, see [DOCUMENTATION.md](DOCUMENTATION.md).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Database and Caching Setup](#database-and-caching-setup)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [Project Structure](#project-structure)

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
|-------------|---------|-------------------------------|
| Python      | 3.10+   | Django backend runtime          |
| Node.js     | 18+     | Angular frontend runtime        |
| PostgreSQL  | 14+     | Primary database                |
| Redis       | 7+      | Caching and Celery message broker |
| Angular CLI | 19+     | Frontend build tooling          |

**Windows-specific requirements:**
- Redis is not natively supported on Windows. Install it via **WSL (Windows Subsystem for Linux)**.
- To install WSL, open PowerShell as Administrator and run: `wsl --install`, then restart your computer.

---

## Backend Setup

### 1. Create and activate a virtual environment

```bash
cd backend
python -m venv ../venv
```

Activate the virtual environment:

```powershell
# PowerShell
..\venv\Scripts\Activate.ps1

# Command Prompt
..\venv\Scripts\activate.bat
```

If you get an execution policy error in PowerShell, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Python dependencies

```bash
pip install django djangorestframework psycopg2-binary django-redis ^
            requests django-cors-headers celery redis drf-yasg
```

### 3. Configure environment variables

Create a `.env` file in the `backend/` directory by copying the example:

```bash
copy .env.example .env
```

Edit `backend/.env` with your values:

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

Get a free News API key at [https://newsapi.org/](https://newsapi.org/).

The `.env` file is already listed in `.gitignore` and will not be committed to version control.

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

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start the development server

```bash
npx ng serve
```

The app will be available at `http://localhost:4200/`.

---

## Database and Caching Setup

### PostgreSQL Setup (Windows)

1. Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/).
2. During installation, note the password you set for the `postgres` user.
3. Open **pgAdmin** or use the command line.

**Using the command line:**
```bash
psql -U postgres
```

```sql
CREATE USER db_user WITH PASSWORD 'your_db_password';
CREATE DATABASE news_dashboard OWNER db_user;
ALTER USER db_user CREATEDB;
\q
```

### Redis Setup (WSL)

Redis must be run through WSL on Windows.

Open your WSL terminal and run:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
redis-cli ping   # Should return PONG
```

You must start Redis in WSL each time before running the application:
```bash
sudo service redis-server start
```

### Celery Worker (for periodic news fetching)

Celery Beat is configured to fetch news every **30 minutes** automatically.

Open two separate terminals and run:

**Terminal — Celery Worker:**
```bash
cd backend
..\venv\Scripts\Activate.ps1
celery -A backend worker --loglevel=info --pool=solo
```

**Terminal — Celery Beat Scheduler:**
```bash
cd backend
..\venv\Scripts\Activate.ps1
celery -A backend beat --loglevel=info
```

The `--pool=solo` flag is required on Windows.

---

## Running the Application

Start all required services in the following order:

**Step 1 — Start Redis** (WSL terminal):
```bash
sudo service redis-server start
```

**Step 2 — Start Django backend** (new terminal):
```bash
cd backend
..\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Step 3 — Start Angular frontend** (new terminal):
```bash
cd frontend
npx ng serve
```

**Step 4 — Open your browser:**
```
http://localhost:4200
```

---

## API Endpoints

| Method | Endpoint                   | Description                        |
|--------|----------------------------|------------------------------------|
| GET    | `/api/news/articles/`      | List articles (paginated, 50/page) |
| GET    | `/api/news/articles/<id>/` | Get article details                |
| GET    | `/api/news/categories/`    | List all categories                |
| GET    | `/api/news/sources/`       | List all sources                   |
| POST   | `/api/news/fetch/`         | Manually trigger news fetch        |

**Query parameters for `/api/news/articles/`:**

| Parameter  | Type   | Description                                |
|------------|--------|--------------------------------------------|
| `page`     | int    | Page number (default: 1)                   |
| `category` | string | Filter by category (e.g. `technology`)     |
| `source`   | string | Filter by source ID (e.g. `bbc-news`)      |
| `country`  | string | Filter by country code (e.g. `us`)         |
| `search`   | string | Full-text search on title and description  |

**Interactive API documentation:**

| URL                              | Description          |
|----------------------------------|----------------------|
| `http://localhost:8000/swagger/` | Swagger UI           |
| `http://localhost:8000/redoc/`   | ReDoc documentation  |
| `http://localhost:8000/admin/`   | Django Admin panel   |

---

## Project Structure

```
news-dashboard/
├── backend/
│   ├── backend/
│   │   ├── settings.py         # Django settings (DB, cache, CORS, Celery)
│   │   ├── urls.py             # Root URL configuration
│   │   ├── celery.py           # Celery app configuration
│   │   └── wsgi.py             # WSGI entry point
│   ├── news/
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
│   │   │       └── fetch_news.py
│   │   └── migrations/
│   │       ├── 0001_initial.py
│   │       └── 0002_database_optimization.py
│   └── manage.py
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

## Author

Lamia Ben Salem
