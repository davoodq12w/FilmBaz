# 🎬 FilmBaz

A full-stack movie and series platform built with Django, featuring real-time live support, advanced PostgreSQL search, Redis caching, and a production-ready multi-service architecture.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Database Bootstrap](#database-bootstrap)
- [API](#api)
- [Performance Optimizations](#performance-optimizations)
- [Live Support System](#live-support-system)

---

## Overview

FilmBaz is a modular Django-based platform for browsing and managing movies and series. Beyond a typical catalog, it includes a full user management system, an advanced fuzzy search engine powered by PostgreSQL trigrams, a Redis-backed caching layer, and a real-time live support chat built on Django Channels and WebSocket — all containerized and configured for production deployment.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django + Django REST Framework |
| HTTP Server | Gunicorn (WSGI) |
| WebSocket Server | Daphne (ASGI) |
| Real-Time | Django Channels |
| Database | PostgreSQL |
| Cache & Channel Layer | Redis |
| Task Queue | Celery Worker + Celery Beat |
| Message Broker | RabbitMQ |
| Reverse Proxy | Nginx |
| Containerization | Docker + Docker Compose |

---

## Architecture

### Hybrid WSGI + ASGI

FilmBaz runs two parallel application servers to handle different traffic types:

```
Standard HTTP Requests:
Browser → Nginx → Gunicorn → Django (WSGI)

WebSocket / Real-Time:
Browser → Nginx → Daphne → Django Channels (ASGI)
```

### Service Map (Docker Compose)

```
filmbaz_web       → Gunicorn (HTTP)
filmbaz_ws        → Daphne (WebSocket)
filmbaz_db        → PostgreSQL
filmbaz_redis     → Redis (Cache + Channel Layer)
filmbaz_rabbitmq  → RabbitMQ (Message Broker)
celery_support_worker → Celery Worker
celery_beat       → Celery Beat (Scheduler)
nginx             → Reverse Proxy
```

### Redis Dual Role

Redis serves two independent purposes in this project:

- **Cache Layer** — Caches movie listings and movie detail pages with dynamic SHA-256 keys to reduce database load.
- **Channel Layer** — Routes WebSocket messages between Django Channels consumers for real-time communication.

---

## Features

### 🎥 Movie & Series Management

- Movie and series catalog with full metadata (title, original title, slug, description, rating, release date, country, duration, content type, age rating)
- Automatic poster (`300×400`) and backdrop (`1600×900`) resizing and cropping on upload
- Genre categorization with many-to-many relationships
- Homepage sections for latest and top-rated content
- Sorting by rating and release date
- Filtering by genre, release year, and age rating

### 🔍 Advanced Search Engine

- **PostgreSQL Trigram Search** (`pg_trgm` extension) for fuzzy and similarity-based matching
- Approximate matching — searching `Interstelar` returns results for `Interstellar`
- Similarity ranking for result ordering
- Significantly more accurate than standard `icontains` lookup

### 👥 Cast & Crew System

- Separate `Cast` (actors) and `Crew` (directors, producers, writers) models
- Role-based crew system — extensible without schema changes
- Many-to-many relationships via explicit through models (`MovieCast`, `MovieCrew`)
- Normalized structure — a cast or crew member is stored once regardless of how many films they appear in
- Automatic image resizing for actor and crew profile photos

### 👤 User Management

**Authentication**
- Custom user model (`FilmBazUser` extending `AbstractBaseUser`)
- Custom `FilmBazUserManager` for full control over user creation
- Registration, login, logout
- Password reset via email link with secure token generation
- Password change for authenticated users

**Profile**
- Editable profile with username, email, phone number
- Profile image upload with automatic resizing and cropping
- Personal dashboard

**Validation (server-side)**
- Username: alphanumeric + underscore only
- Phone: 11-digit Iranian format starting with `09`, uniqueness enforced
- Email: format validation + uniqueness enforced
- Password: confirmation match check

### 💾 Watchlist

- Users can save and remove movies from a personal watchlist
- Saved movies list accessible from the user dashboard

### 💬 Comment System

- Comments linked to movies and authenticated users
- Ordered by most recent
- Ajax-rendered for smooth interaction

### 🎫 Ticket System

- Users can submit feedback in three categories: Criticism, Proposal, Report
- Automatic confirmation email sent upon ticket submission

### 📡 Live Support System

See [Live Support System](#live-support-system) section for full details.

---

## Project Structure

```
FilmBaz/
├── FilmBaz/               # Project core (settings, urls, asgi, wsgi, celery)
├── account/               # User model, auth, profile, tickets, watchlist
├── film/                  # Movies, genres, comments, search, caching
├── people/                # Cast and crew models and relations
├── support/               # Live chat, WebSocket consumers, session management
├── templates/
│   ├── base.html
│   ├── account/
│   ├── film/
│   ├── people/
│   └── support/
├── static/
├── media/
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
└── entrypoint.sh
```

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Run the Project

```bash
git clone https://github.com/davoodq12w/FilmBaz.git
cd FilmBaz
docker compose up --build
```

The `entrypoint.sh` will automatically run migrations and seed the database on first startup.

### Access

| Service | URL |
|---|---|
| Web App | http://localhost |
| Django Admin | http://localhost/admin |

---

## Database Bootstrap

FilmBaz includes a custom data import pipeline that seeds the database automatically on first run via Django management commands. The import order follows dependency constraints:

```
1. load_genres       → Genre records
2. load_casts        → Actor profiles
3. load_crews        → Director / Producer / Writer profiles
4. load_movies       → Movie and series records
5. load_relations    → Movie ↔ Cast / Crew links
6. load_pictures     → Poster and backdrop images
```

This pipeline is executed automatically via `entrypoint.sh` but can also be run manually:

```bash
docker compose exec web python manage.py load_genres
docker compose exec web python manage.py load_casts
docker compose exec web python manage.py load_crews
docker compose exec web python manage.py load_movies
docker compose exec web python manage.py load_relations
docker compose exec web python manage.py load_pictures
```

---

## API

Django REST Framework is integrated and available under `/api-auth/`. Full API endpoint documentation is available in the project wiki.

---

## Performance Optimizations

### Redis Caching

- Movie listing pages cached with dynamic SHA-256 keys based on query parameters (filters, sorting, pagination)
- Movie detail pages and comments cached individually
- Cache invalidated on data updates

### Query Optimization

- `select_related()` and `prefetch_related()` used throughout to eliminate N+1 query problems on relational data (movies → genres, movies → cast, movies → crew)

### Image Optimization

- All uploaded images (posters, backdrops, profile photos, cast/crew photos) are automatically resized and cropped at upload time using `ResizedImageField`
- Reduces storage consumption and page load time

### PostgreSQL Trigram Search

- `pg_trgm` extension enabled at the database level
- Enables fast, similarity-ranked full-text search without an external search engine

---

## Live Support System

FilmBaz includes a production-grade real-time support chat built on Django Channels.

### How It Works

```
User
  │
  ▼
WebSocket Connection
  │
  ▼
Daphne (ASGI Server)
  │
  ▼
Django Channels Consumer
  │
  ▼
Redis Channel Layer
  │
  ▼
Support Agent Consumer
```

### Features

- **Real-time messaging** via `AsyncWebsocketConsumer` — no page refresh needed
- **Session-based chat** — each conversation is stored in a `SupportSession` with `OPEN` / `CLOSED` state
- **Persistent history** — all messages stored in `SupportMessage` with sender, content, timestamp, and read status
- **Read tracking** — `is_read` field on each message enables unread indicators
- **Authenticated connections** — `AuthMiddlewareStack` ensures only logged-in users can open WebSocket channels
- **Isolated channel groups** — each session gets its own Redis channel group (`session_<id>`), so messages are never mixed between users

### Scheduled Session Cleanup

Inactive support sessions are automatically closed by a background task:

```
Celery Beat (Scheduler)
  │
  ▼
RabbitMQ (Message Broker)
  │
  ▼
Celery Worker
  │
  ▼
Auto-close stale OPEN sessions
```

### Scalability

- Redis-backed channel layer supports multi-instance deployment
- Async consumers handle high concurrency without blocking threads
- Decoupled from HTTP traffic via separate Daphne server

---

## License

MIT
