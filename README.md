# Latest News Dashboard

A full-stack web application that fetches, stores, caches, and displays news articles from NewsAPI.

## Overview

This project demonstrates a scalable news aggregation system with:
- Real-time news fetching from NewsAPI
- PostgreSQL database with optimized indexing
- Redis caching layer for performance
- Celery background tasks for automated updates
- RESTful API with filtering and search
- Responsive Angular frontend

## Tech Stack

- **Backend:** Django 4.x, Django REST Framework
- **Frontend:** Angular 19+
- **Database:** PostgreSQL 14+
- **Cache:** Redis 7+
- **Task Queue:** Celery + Celery Beat
- **API Documentation:** Swagger (drf-yasg)

## Prerequisites

Ensure you have the following installed on Windows:

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (via WSL)
- Git

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/fawoenix/latest-news-dashboard.git
cd news-dashboard
```

### 2. Setup PostgreSQL

```bash
psql -U postgres
```

```sql
CREATE USER news_user WITH PASSWORD 'secure_password';
CREATE DATABASE news_dashboard OWNER news_user;
\q
```

### 3. Setup Redis (WSL)

```bash
wsl --install
# After restart, open WSL:
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### 4. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file in backend/ directory
# Copy contents from .env.example and update values

# Run migrations
cd backend
python manage.py migrate

# Fetch initial data
python manage.py fetch_news --all-categories

# Start server
python manage.py runserver
```

Backend runs at: http://127.0.0.1:8000

### 5. Frontend Setup

```bash
# In a new terminal
cd frontend
npm install
npx ng serve
```

Frontend runs at: http://localhost:4200

## Running the Application

### Minimum Required Services

**Terminal 1 - Redis (WSL):**
```bash
wsl
sudo service redis-server start
```

**Terminal 2 - Django Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Terminal 3 - Angular Frontend:**
```bash
cd frontend
npx ng serve
```

### Optional: Background Tasks (Celery)

**Terminal 4 - Celery Worker:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
celery -A backend worker --loglevel=info --pool=solo
```

**Terminal 5 - Celery Beat:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
celery -A backend beat --loglevel=info
```

## API Documentation

Access interactive API documentation:
- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

## Project Structure

```
news-dashboard/
├── backend/
│   ├── backend/          # Django project settings
│   ├── news/             # News app (models, views, serializers)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/app/
│   ├── package.json
│   └── angular.json
├── README.md
└── DOCUMENTATION.md
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

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

## Common Issues

### Virtual Environment Activation Error (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### Redis Not Starting
```bash
wsl
sudo service redis-server restart
redis-cli ping
```

## Testing

Run backend tests:
```bash
cd backend
python manage.py test
```

## Documentation

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

Includes:
- Complete setup guide
- Database configuration and optimization
- Caching strategy
- API endpoints reference
- Architecture details
- Troubleshooting guide

## Author

**Lamia Ben Salem**

## License

This project is licensed under the MIT License.
