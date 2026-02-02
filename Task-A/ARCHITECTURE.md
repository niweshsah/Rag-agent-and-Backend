# Me-API Playground - System Architecture

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │          Streamlit Frontend (Port 8501)                 │    │
│  │  - Profile Card Component                               │    │
│  │  - Search Interface                                     │    │
│  │  - Projects/Work Experience List                        │    │
│  │  - Admin Panel (Profile Update)                         │    │
│  └─────────────────┬──────────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (Port 8000)                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              FastAPI Backend                            │    │
│  │                                                          │    │
│  │  Routes:                                                │    │
│  │  • GET  /health                                         │    │
│  │  • GET  /profile                                        │    │
│  │  • PUT  /profile (Auth Required)                        │    │
│  │  • GET  /projects?skill=X                               │    │
│  │  • GET  /skills/top                                     │    │
│  │  • GET  /search?q=...                                   │    │
│  │                                                          │    │
│  │  Middleware:                                            │    │
│  │  • CORS Configuration                                   │    │
│  │  • Basic Auth (for updates)                             │    │
│  │  • Error Handling                                       │    │
│  └─────────────────┬──────────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────────┘
                     │ SQLAlchemy ORM
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL Database                        │    │
│  │                                                          │    │
│  │  Tables:                                                │    │
│  │  • profiles (1)                                         │    │
│  │  • education (n)                                        │    │
│  │  • work_experience (n)                                  │    │
│  │  • projects (n)                                         │    │
│  │  • skills (n)                                           │    │
│  │  • social_links (n)                                     │    │
│  │  • project_skills (n:m junction)                        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│    profiles     │
├─────────────────┤
│ id (PK)         │◄────────┐
│ name            │         │
│ email           │         │
│ phone           │         │
│ location        │         │
│ bio             │         │
│ created_at      │         │
│ updated_at      │         │
└─────────────────┘         │
                            │
                            │ 1:n
         ┌──────────────────┼──────────────────┬──────────────────┬──────────────────┐
         │                  │                  │                  │                  │
         │                  │                  │                  │                  │
┌────────▼────────┐ ┌───────▼──────┐ ┌─────────▼────────┐ ┌──────▼───────┐ ┌──────▼───────┐
│   education     │ │    skills    │ │ work_experience  │ │   projects   │ │social_links  │
├─────────────────┤ ├──────────────┤ ├──────────────────┤ ├──────────────┤ ├──────────────┤
│ id (PK)         │ │ id (PK)      │ │ id (PK)          │ │ id (PK)      │ │ id (PK)      │
│ profile_id (FK) │ │ profile_id   │ │ profile_id (FK)  │ │ profile_id   │ │ profile_id   │
│ institution     │ │   (FK)       │ │ company          │ │   (FK)       │ │   (FK)       │
│ degree          │ │ name         │ │ position         │ │ name         │ │ platform     │
│ field           │ │ level        │ │ description      │ │ description  │ │ url          │
│ start_date      │ │ category     │ │ start_date       │ │ url          │ │ icon         │
│ end_date        │ │ years_exp    │ │ end_date         │ │ github_url   │ └──────────────┘
│ gpa             │ └──────────────┘ │ is_current       │ │ demo_url     │
└─────────────────┘         │        └──────────────────┘ │ start_date   │
                            │                             │ end_date     │
                            │                             │ status       │
                            │                             └──────────────┘
                            │                                    │
                            │                                    │
                            │         n:m                        │
                            │    ┌─────────────────┐             │
                            └────►project_skills   ◄─────────────┘
                                 ├─────────────────┤
                                 │ project_id (FK) │
                                 │ skill_id (FK)   │
                                 │ PRIMARY KEY     │
                                 │ (both columns)  │
                                 └─────────────────┘
```

## 📊 Data Flow

### GET /profile Flow
```
User → Streamlit UI → GET /profile → FastAPI Handler
                                          │
                                          ▼
                                    Query Database
                                          │
                                          ▼
                                    Join all tables
                                    (profile + education +
                                     work + projects +
                                     skills + social)
                                          │
                                          ▼
                                    JSON Response ← User receives data
```

### POST /search Flow
```
User Input → Streamlit Search → GET /search?q=term → FastAPI Handler
                                                           │
                                                           ▼
                                                    Full-text search
                                                    across projects
                                                    and work_experience
                                                           │
                                                           ▼
                                                    Filter & rank results
                                                           │
                                                           ▼
                                                    JSON Response ← Display results
```

### PUT /profile Flow
```
Admin → Streamlit Admin Panel → PUT /profile + Auth Header → Validate Auth
                                                                    │
                                                                    ▼
                                                              Parse JSON
                                                                    │
                                                                    ▼
                                                              Validate data
                                                                    │
                                                                    ▼
                                                              Update DB
                                                              (transaction)
                                                                    │
                                                                    ▼
                                                              Return updated
                                                              profile ← Success
```

## 🔐 Security Layers

1. **CORS**: Configured to allow Streamlit origin
2. **Basic Auth**: Required for PUT/POST operations (Base64 encoded credentials)
3. **Input Validation**: Pydantic models validate all inputs
4. **SQL Injection**: SQLAlchemy ORM prevents injection attacks
5. **Rate Limiting**: (Optional) Can be added via middleware

## 🚀 Deployment Architecture

### Development
```
localhost:8000  → FastAPI Backend
localhost:8501  → Streamlit Frontend
localhost:5432  → PostgreSQL (Docker)
```

### Production (Recommended)
```
render.com      → FastAPI Backend (Free tier)
streamlit.io    → Streamlit Frontend (Free)
render.com      → PostgreSQL Database (Free tier)
```

### Alternative Options
```
Railway.app     → Full Stack (Backend + DB)
Fly.io          → Backend + DB
Vercel          → Cannot host Streamlit (static only)
```

## 📦 Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend | FastAPI | Fast, modern, auto-docs, async support |
| Database | PostgreSQL | Relational data, ACID compliance, free tiers |
| ORM | SQLAlchemy | Mature, type-safe, migration support |
| Frontend | Streamlit | Rapid development, Python-native, minimal code |
| Auth | Basic Auth | Simple, sufficient for demo, easy to upgrade |
| Hosting | Render | Free tier, easy deployment, PostgreSQL included |

## 🎯 Key Features

- **Clean Architecture**: Separation of concerns (routes, services, models)
- **Type Safety**: Pydantic models for validation
- **Auto Documentation**: FastAPI generates OpenAPI/Swagger docs
- **Real-time Search**: Full-text search across content
- **Skill Analytics**: Aggregation queries for top skills
- **Modular Design**: Easy to extend and maintain
