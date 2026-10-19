# 🎬 FilmBaz

<p align="center">

A production-oriented movie streaming platform built with a **Microservice Architecture**, featuring **Django**, *
*FastAPI**, **Machine Learning**, **WebSockets**, **Celery**, and **Docker**.

</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white"/>  
  <img src="https://img.shields.io/badge/DRF-black?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"/>
  <img src="https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white"/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white"/>
  <img src="https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white"/>
  <img src="https://img.shields.io/badge/Regex-FF69B4?style=for-the-badge&logo=codio&logoColor=white"/>
  <img src="https://img.shields.io/badge/Unittest-6E40C9?style=for-the-badge&logo=pytest&logoColor=white"/>
  <img src="https://img.shields.io/badge/WebSocket-00BFFF?style=for-the-badge&logo=websockets&logoColor=white"/>
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
</p>

---

## 📖 About

FilmBaz is a full-stack movie streaming platform designed to simulate a real-world production environment.

Instead of relying on a monolithic architecture, the project is divided into multiple independent services responsible
for web requests, real-time communication, asynchronous processing, caching, machine learning, and deployment.

The platform demonstrates how modern backend technologies can work together to build a scalable and maintainable
application.

### Key Highlights

- 🏛 Microservice Architecture
- 🤖 AI-Powered Recommendation System
- 💬 Real-Time Support Chat
- ⚡ Asynchronous Background Processing
- 🔍 PostgreSQL Trigram Search
- 📦 Fully Dockerized Environment
- 🔐 JWT Authentication
- 📺 Custom Video Player
- 📊 User Interaction Analytics
- 🚀 Production-Oriented Design

---

## 📚 Table of Contents

- [Core Features](#-core-features)
- [Technology Stack](#-technology-stack)
- [Microservice Architecture](#-microservice-architecture)
- [Docker Services](#-docker-services)
- [Recommendation System](#-recommendation-system)
- [Background Tasks](#-background-tasks)
- [Performance Optimizations](#-performance-optimizations)
- [REST API](#-rest-api)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Developer](#-developer)

---

# 🛠 Technology Stack

| Category         | Technologies                    |
|------------------|---------------------------------|
| Backend          | Django 5, Django REST Framework |
| Machine Learning | FastAPI                         |
| Database         | PostgreSQL                      |
| Cache            | Redis                           |
| Message Broker   | RabbitMQ                        |
| Background Tasks | Celery, Celery Beat             |
| WebSocket        | Django Channels, Daphne         |
| Reverse Proxy    | Nginx                           |
| Deployment       | Docker, Docker Compose          |
| Authentication   | JWT                             |
| Search           | PostgreSQL Trigram Search       |
| Image Processing | django-resized                  |

---

# ✨ Core Features

### 👤 User Management

- Custom User Model
- JWT Authentication
- Registration & Login
- Password Reset
- Profile Management
- Favorite Genres

### 🎬 Movie Platform

- Movies & TV Series
- Movie Details
- Genres
- Comments
- Likes
- Watchlist
- Watch Progress
- Advanced Search
- Pagination
- Filtering & Sorting

### 💬 Support System

- Real-Time Chat
- WebSocket Communication
- Session Management
- Read Receipts
- Ticket System

### 🤖 Machine Learning

- Personalized Recommendations
- Automatic Dataset Generation
- Nightly Model Training
- Model Evaluation
- Recommendation Storage

### ⚙ Backend Infrastructure

- Dockerized Services
- Redis Caching
- Celery Background Tasks
- Scheduled Jobs
- Database Audit Logging
- PostgreSQL Trigram Search
- Custom Management Commands

---

# 🏗 Microservice Architecture

FilmBaz is built around a microservice architecture where each service has a single responsibility and runs inside its
own Docker container.

This separation improves scalability, maintainability, and allows each component to evolve independently.

```
                            Client
                               │
                 HTTP / WebSocket Requests
                               │
                         ┌────────────┐
                         │   Nginx    │
                         └─────┬──────┘
               ┌───────────────┼────────────────┐
               │               │                │
               ▼               ▼                ▼
        Django Backend     WebSocket       ML Service
         (Gunicorn)         (Daphne)       (FastAPI)
               │               │
               ├──────┐   ┌────┘
               ▼      ▼   ▼
          PostgreSQL  Redis
               ▲          ▲
               │          │
         Celery Worker ───┘
               ▲
               │
          RabbitMQ
               ▲
               │
          Celery Beat
```

---

## 🎯 Design Principles

The architecture is based on the following principles:

- **Separation of Responsibilities** – Each service focuses on a specific task.
- **Loose Coupling** – Services communicate through APIs, WebSockets, or message queues.
- **Scalability** – Individual services can be scaled independently.
- **Maintainability** – Isolated services simplify development and debugging.
- **Containerization** – Every service runs inside its own Docker container.

---

# 🐳 Docker Services

FilmBaz consists of multiple Docker containers working together.

| Service           | Description                                                                    |
|-------------------|--------------------------------------------------------------------------------|
| **filmbaz**       | Main Django application serving web pages and REST APIs.                       |
| **filmbaz_ws**    | Dedicated ASGI service responsible for WebSocket communication.                |
| **ml_service**    | FastAPI service responsible for training and serving the recommendation model. |
| **postgres**      | Primary PostgreSQL database.                                                   |
| **redis**         | Cache storage and Django Channels backend.                                     |
| **rabbitmq**      | Message broker used by Celery.                                                 |
| **celery_worker** | Executes asynchronous tasks.                                                   |
| **celery_beat**   | Schedules periodic background jobs.                                            |
| **nginx**         | Reverse proxy that routes HTTP and WebSocket requests.                         |

---

# 🔄 Request Flow

### HTTP Request

```
Client
   │
   ▼
Nginx
   │
   ▼
Gunicorn
   │
   ▼
Django
   │
   ▼
PostgreSQL
```

---

### WebSocket Request

```
Client
   │
   ▼
Nginx
   │
   ▼
Daphne
   │
   ▼
Django Channels
   │
   ▼
Redis
```

---

### Background Task Flow

```
Application
     │
     ▼
 RabbitMQ
     │
     ▼
Celery Worker
     │
     ▼
Task Execution
```

---

# 🤖 Recommendation System

One of the core components of FilmBaz is an independent recommendation service built with **FastAPI**.

Unlike the main Django application, the recommendation engine is isolated into its own service, allowing machine
learning workloads to run independently of user requests.

The recommendation pipeline consists of the following stages:

1. User interactions are collected by the backend.
2. Interaction data is transformed into training datasets.
3. A scheduled task starts the training process.
4. The new model is evaluated.
5. If the new model performs better than the current one, it replaces the previous model.
6. Personalized movie recommendations are generated and stored for users.

This architecture keeps computationally intensive machine learning tasks separate from the main application, improving
responsiveness and scalability.

---

# ⚡ Performance Optimizations

FilmBaz includes multiple optimization techniques to improve performance, reduce database load, and provide a smoother
user experience.

## 🚀 Redis Caching

Redis is used to cache frequently requested data and reduce database queries.

Caching is applied to:

- Movie list pages
- Movie details
- Movie comments

This significantly reduces response time for frequently accessed resources.

---

## 🗄 Database Optimization

Database queries are optimized using Django ORM best practices.

Optimization techniques include:

- `select_related()`
- `prefetch_related()`

These techniques minimize unnecessary database queries and reduce N+1 query problems.

---

## 🔍 Intelligent Search

FilmBaz uses PostgreSQL's **pg_trgm** extension to provide fuzzy searching capabilities.

Features include:

- Typo tolerance
- Similarity search
- Search ranking
- Partial matching

For example:

```
Interstelar
```

can successfully return:

```
Interstellar
```

---

## 🖼 Image Optimization

Uploaded images are automatically processed before storage.

Supported image types:

- Movie Posters
- Movie Backdrops
- User Profile Images
- Cast Images
- Crew Images

Image optimization reduces storage usage while improving page loading speed.

---

# 🔄 Background Tasks

Time-consuming operations are executed asynchronously using **Celery** and **RabbitMQ**, preventing users from waiting
for long-running processes.

## Asynchronous Tasks

Examples include:

- Sending support ticket confirmation emails
- Sending password reset emails
- Delivering real-time support messages

---

## Scheduled Tasks

Periodic tasks are executed automatically using **Celery Beat**.

Current scheduled jobs include:

- Closing expired support sessions
- Building a new recommendation dataset
- Training a new recommendation model
- Generating personalized recommendations

These tasks are scheduled during off-peak hours to minimize system load.

---

# 🌐 REST API

FilmBaz provides a comprehensive REST API built with Django REST Framework.

Main API modules include:

| Module          | Description                             |
|-----------------|-----------------------------------------|
| Authentication  | Login, Registration, JWT Authentication |
| Users           | Profile Management, Favorite Genres     |
| Movies          | Movies, Details, Search, Filtering      |
| Genres          | Available Movie Genres                  |
| Comments        | Movie Comments                          |
| Recommendations | Personalized Recommendations            |
| Support         | Support Sessions & Chat                 |

The APIs are designed for both web and mobile applications.

---

# 🔐 Security

Security has been considered throughout the application.

Implemented security features include:

- Custom User Model
- JWT Authentication
- Secure Password Management
- Server-side Validation
- Authenticated WebSocket Connections
- Permission-based API Access
- Protected User Resources

---

# 📊 Audit Logging

FilmBaz includes an audit logging system that records database changes.

The logging system tracks:

- Object Creation
- Object Updates
- Object Deletion

This helps simplify debugging, monitoring, and future auditing of application behavior.

---

# 📂 Project Structure

The project is organized into multiple independent services.

```text
FilmBaz
│
├── filmbaz/              # Django Backend
├── filmbaz_ws/           # WebSocket Service
├── ml_service/           # Machine Learning Service
├── nginx/                # Reverse Proxy
├── postgres/             # Database
├── docker-compose.yml
└── README.md
```

The Django backend itself follows a modular architecture with dedicated applications for authentication, movies,
analytics, support, people management, and logging.

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/davoodq12w/FilmBaz.git
cd FilmBaz
```

---

## Start Services

```bash
docker compose up --build
```

All required services will start automatically.

---

## Default Administrator

During the initial startup, the project automatically creates a default administrator account.

| Username |   | Password     |
|----------|:--|--------------|
| root     |   | rootpassword |

This account is intended for development purposes only.

---

# 🧪 Testing

The project includes unit tests covering the core parts of the application.

Test coverage includes:

- Models
- Views
- Forms
- Serializers
- Consumers

Run all tests:

```bash
python manage.py test
```

---

# 🎯 Project Goals

FilmBaz was developed to demonstrate modern backend development concepts rather than simply providing a movie website.

The project focuses on:

- Microservice Architecture
- Clean Project Structure
- Scalable Backend Design
- Asynchronous Processing
- Real-Time Communication
- Recommendation Systems
- Containerized Deployment

---

# 📄 License

This project is licensed under the MIT License.

See the LICENSE file for more information.

---

# 👨‍💻 Developer

**Davood Rashi**

Backend Developer specializing in Django, Python, and scalable backend systems.

GitHub:
https://github.com/davoodq12w

---

⭐ If you found this project useful, consider giving it a star.