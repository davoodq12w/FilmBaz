# 🎬 FilmBaz

FilmBaz is a modular movie and series platform built with Django, designed to provide a scalable and production-ready environment for content management, user interaction, and real-time customer support.

The platform goes beyond a traditional movie catalog by integrating advanced search capabilities, real-time communication, background task processing, caching mechanisms, and a containerized deployment architecture.

---

# ✨ Key Features

## User Management

* Custom User Model
* User Registration & Authentication
* Profile Management
* Profile Image Upload
* Password Reset & Password Change
* User Dashboard
* Saved Movies (Watchlist)

## Movie Management

* Movie & Series Catalog
* Genre Categorization
* Movie Details Page
* Poster & Backdrop Images
* Release Date Tracking
* Rating System
* Country & Runtime Information

## Community Features

* Comment System
* User Watchlist
* User Feedback & Ticket Submission

## Cast & Crew Management

* Actor Profiles
* Director Management
* Producer Management
* Writer Management
* Scalable Many-to-Many Relationships

## Real-Time Support System

* Live Support Chat
* WebSocket Communication
* Session-Based Messaging
* Read Status Tracking
* Persistent Conversation History

---

# 🏗 Architecture

FilmBaz follows a modular architecture and separates responsibilities into independent applications.

```text
FilmBaz
│
├── account     → User Management
├── film        → Movies & Genres
├── people      → Cast & Crew
├── support     → Real-Time Support
└── core        → Project Configuration
```

The project utilizes a hybrid architecture:

```text
HTTP Requests
      │
      ▼
 Gunicorn (WSGI)
      │
      ▼
    Django

WebSocket Requests
      │
      ▼
 Daphne (ASGI)
      │
      ▼
 Django Channels
```

---

# 🔍 Advanced Search Engine

FilmBaz uses PostgreSQL Trigram Search (`pg_trgm`) to provide fuzzy searching capabilities.

Features:

* Similarity Search
* Approximate Matching
* Typo Tolerance
* Search Ranking

Example:

Searching for:

Interstelar

can still return:

Interstellar

---

# ⚡ Performance Optimizations

The platform includes several optimizations to improve scalability and response times:

### Redis Caching

* Movie List Caching
* Movie Detail Caching
* Comment Caching

### Database Optimization

* select_related()
* prefetch_related()
* Reduced N+1 Query Issues

### Image Optimization

Automatic image resizing for:

* Movie Posters
* Movie Backdrops
* User Avatars
* Actor Images
* Crew Images

---

# 💬 Real-Time Support System

The support module is built using:

* Django Channels
* Redis Channel Layer
* Daphne
* WebSockets

Capabilities:

* Real-Time Messaging
* Authenticated Connections
* Session-Based Communication
* Read Receipts
* Persistent Chat History

---

# 🔄 Background Task Processing

FilmBaz uses Celery and RabbitMQ for asynchronous processing.

Tasks include:

* Scheduled Session Cleanup
* Automatic Support Session Closure
* Background Processing
* Scheduled Jobs

Architecture:

```text
Celery Beat
     │
     ▼
 RabbitMQ
     │
     ▼
 Celery Worker
```

---

# 🗄 Database Design

Main entities:

* FilmBazUser
* Movie
* Genre
* Comment
* Cast
* Crew
* MovieCast
* MovieCrew
* SupportSession
* SupportMessage
* Ticket

Design principles:

* Normalized Relationships
* Through Models
* Reusable Records
* Scalable Data Structure

---

# 🚀 Database Bootstrap

The project contains custom management commands for automated database initialization.

Available commands:

* load_genres
* load_casts
* load_crews
* load_movies
* load_relations
* load_pictures

This enables rapid deployment and repeatable environment setup.

---

# 🐳 Deployment Stack

FilmBaz is designed for production environments.

Infrastructure:

* Django 5
* PostgreSQL
* Redis
* RabbitMQ
* Celery
* Django Channels
* Gunicorn
* Daphne
* Nginx
* Docker
* Docker Compose

---

# 🛠 Installation

## Clone Repository

```bash
git clone https://github.com/davoodq12w/FilmBaz.git
cd FilmBaz
```

## Run with Docker

```bash
docker compose up --build
```

The application and all required services will start automatically.

---

# 🔐 Security

* Custom Authentication System
* Login Protected Views
* Authenticated WebSocket Connections
* Form-Level Validation
* Secure Password Management

---

# 👨‍💻 Developer

Developed by Davood Rashi

Backend Developer | Django Developer | DevOps Enthusiast
