# Me-API Playground

A live, queryable resume/portfolio REST API built with FastAPI, designed to expose personal profile data through a structured, type-safe API interface. This project includes a full-featured backend with CRUD operations and an interactive Streamlit frontend for visualization.

---

## Table of Contents

- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Local Setup](#local-setup)
- [Deployment](#deployment)
- [Sample cURL Commands](#sample-curl-commands)
- [Authentication](#authentication)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)

---

## Architecture

```
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|  Streamlit UI     +------>+  FastAPI Backend  +------>+  PostgreSQL DB    |
|  (Frontend)       |       |  (REST API)       |       |  (Data Layer)     |
|  Port: 8501       |       |  Port: 8000       |       |  Port: 5432       |
|                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+
```

### Technology Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | FastAPI 0.109.0, Uvicorn            |
| Database   | PostgreSQL, SQLAlchemy 2.0.25       |
| ORM        | SQLAlchemy with Pydantic validation |
| Frontend   | Streamlit 1.53.1, Plotly            |
| Auth       | HTTP Basic Authentication           |
| Deployment | Render (Backend), Streamlit Cloud   |

### Key Design Decisions

- **Single Profile Model**: The API is designed around a single user profile, making it ideal for personal portfolio use cases
- **Relational Data Model**: Education, work experience, projects, skills, and social links are separate entities with foreign key relationships
- **Many-to-Many Skills**: Projects can be associated with multiple skills through a junction table
- **Basic Auth for Mutations**: Read operations are public; create, update, and delete operations require authentication

---

## Database Schema

### Entity Relationship Diagram

```
profiles
    |
    +-- education (1:N)
    |
    +-- work_experience (1:N)
    |
    +-- skills (1:N) <----- project_skills (N:M) -----> projects (1:N)
    |
    +-- social_links (1:N)
```

### Table Definitions

#### profiles
| Column      | Type         | Constraints      |
|-------------|--------------|------------------|
| id          | INTEGER      | PRIMARY KEY      |
| name        | VARCHAR(255) | NOT NULL         |
| email       | VARCHAR(255) | NOT NULL, UNIQUE |
| phone       | VARCHAR(50)  | NULLABLE         |
| location    | VARCHAR(255) | NULLABLE         |
| bio         | TEXT         | NULLABLE         |
| created_at  | DATETIME     | DEFAULT NOW      |
| updated_at  | DATETIME     | DEFAULT NOW      |

#### education
| Column      | Type         | Constraints                    |
|-------------|--------------|--------------------------------|
| id          | INTEGER      | PRIMARY KEY                    |
| profile_id  | INTEGER      | FOREIGN KEY (profiles.id)      |
| institution | VARCHAR(255) | NOT NULL                       |
| degree      | VARCHAR(255) | NOT NULL                       |
| field       | VARCHAR(255) | NULLABLE                       |
| start_date  | VARCHAR(50)  | NULLABLE                       |
| end_date    | VARCHAR(50)  | NULLABLE                       |
| gpa         | FLOAT        | NULLABLE (0.0 - 4.0)           |
| description | TEXT         | NULLABLE                       |

#### work_experience
| Column      | Type         | Constraints                    |
|-------------|--------------|--------------------------------|
| id          | INTEGER      | PRIMARY KEY                    |
| profile_id  | INTEGER      | FOREIGN KEY (profiles.id)      |
| company     | VARCHAR(255) | NOT NULL                       |
| position    | VARCHAR(255) | NOT NULL                       |
| description | TEXT         | NULLABLE                       |
| start_date  | VARCHAR(50)  | NULLABLE                       |
| end_date    | VARCHAR(50)  | NULLABLE                       |
| is_current  | BOOLEAN      | DEFAULT FALSE                  |
| location    | VARCHAR(255) | NULLABLE                       |

#### skills
| Column           | Type         | Constraints                    |
|------------------|--------------|--------------------------------|
| id               | INTEGER      | PRIMARY KEY                    |
| profile_id       | INTEGER      | FOREIGN KEY (profiles.id)      |
| name             | VARCHAR(255) | NOT NULL                       |
| level            | VARCHAR(50)  | NULLABLE (beginner/intermediate/advanced/expert) |
| category         | VARCHAR(100) | NULLABLE                       |
| years_experience | FLOAT        | NULLABLE                       |

#### projects
| Column      | Type         | Constraints                    |
|-------------|--------------|--------------------------------|
| id          | INTEGER      | PRIMARY KEY                    |
| profile_id  | INTEGER      | FOREIGN KEY (profiles.id)      |
| name        | VARCHAR(255) | NOT NULL                       |
| description | TEXT         | NULLABLE                       |
| url         | VARCHAR(500) | NULLABLE                       |
| github_url  | VARCHAR(500) | NULLABLE                       |
| demo_url    | VARCHAR(500) | NULLABLE                       |
| start_date  | VARCHAR(50)  | NULLABLE                       |
| end_date    | VARCHAR(50)  | NULLABLE                       |
| status      | VARCHAR(50)  | NULLABLE (completed/in-progress/archived) |

#### social_links
| Column     | Type         | Constraints                    |
|------------|--------------|--------------------------------|
| id         | INTEGER      | PRIMARY KEY                    |
| profile_id | INTEGER      | FOREIGN KEY (profiles.id)      |
| platform   | VARCHAR(100) | NOT NULL                       |
| url        | VARCHAR(500) | NOT NULL                       |
| icon       | VARCHAR(100) | NULLABLE                       |

#### project_skills (Junction Table)
| Column     | Type    | Constraints               |
|------------|---------|---------------------------|
| project_id | INTEGER | FOREIGN KEY (projects.id) |
| skill_id   | INTEGER | FOREIGN KEY (skills.id)   |

---

## API Endpoints

### System
| Method | Endpoint  | Description           | Auth |
|--------|-----------|----------------------|------|
| GET    | /         | API root information | No   |
| GET    | /health   | Health check status  | No   |
| GET    | /docs     | Swagger UI           | No   |
| GET    | /redoc    | ReDoc documentation  | No   |

### Profile
| Method | Endpoint  | Description          | Auth |
|--------|-----------|---------------------|------|
| GET    | /profile  | Get complete profile | No   |
| POST   | /profile  | Create new profile   | Yes  |
| PUT    | /profile  | Update profile       | Yes  |
| DELETE | /profile  | Delete profile       | Yes  |

### Education
| Method | Endpoint              | Description              | Auth |
|--------|-----------------------|-------------------------|------|
| GET    | /education            | List all education      | No   |
| POST   | /education            | Add education record    | Yes  |
| PUT    | /education/{id}       | Update education record | Yes  |
| DELETE | /education/{id}       | Delete education record | Yes  |

### Work Experience
| Method | Endpoint                 | Description                | Auth |
|--------|--------------------------|---------------------------|------|
| GET    | /work-experience         | List all work experience  | No   |
| POST   | /work-experience         | Add work experience       | Yes  |
| PUT    | /work-experience/{id}    | Update work experience    | Yes  |
| DELETE | /work-experience/{id}    | Delete work experience    | Yes  |

### Projects
| Method | Endpoint         | Description                              | Auth |
|--------|------------------|----------------------------------------|------|
| GET    | /projects        | List projects (filter by skill/status) | No   |
| GET    | /projects/{id}   | Get project by ID                      | No   |
| POST   | /projects        | Create project                         | Yes  |
| PUT    | /projects/{id}   | Update project                         | Yes  |
| DELETE | /projects/{id}   | Delete project                         | Yes  |

### Skills
| Method | Endpoint       | Description                    | Auth |
|--------|----------------|-------------------------------|------|
| GET    | /skills        | List all skills               | No   |
| GET    | /skills/top    | Get top skills by project count| No   |
| POST   | /skills        | Add skill                     | Yes  |
| PUT    | /skills/{id}   | Update skill                  | Yes  |
| DELETE | /skills/{id}   | Delete skill                  | Yes  |

### Social Links
| Method | Endpoint            | Description         | Auth |
|--------|---------------------|---------------------|------|
| GET    | /social-links       | List all links      | No   |
| POST   | /social-links       | Add social link     | Yes  |
| PUT    | /social-links/{id}  | Update social link  | Yes  |
| DELETE | /social-links/{id}  | Delete social link  | Yes  |

### Search
| Method | Endpoint     | Description                              | Auth |
|--------|--------------|----------------------------------------|------|
| GET    | /search?q=   | Search across projects and experience  | No   |

---

## Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip or conda for package management

### 1. Clone the Repository

```bash
git clone https://github.com/niweshsah/Predusk-Tasks
cd predusk/Task-A
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/me_api_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

### 5. Set Up PostgreSQL Database

```bash
# Create database
createdb me_api_db

# Or using psql
psql -U postgres -c "CREATE DATABASE me_api_db;"
```

### 6. Run the Backend Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### 7. Seed the Database (Optional)

```bash
python seed.py
```

### 8. Run the Frontend

In a separate terminal:

```bash
cd frontend
streamlit run app.py
```

The frontend will be available at `http://localhost:8501`

---

## Deployment

### Deployed URLs

| Service  | URL                                           |
|----------|-----------------------------------------------|
| Backend  | `https://predusk-backend-ngpt.onrender.com`      |
| Frontend | `https://predusk-api.streamlit.app`       |

### Render Deployment (Backend)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd Task-A/backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `ADMIN_USERNAME`: Admin username
   - `ADMIN_PASSWORD`: Admin password
   - `ALLOWED_ORIGINS`: Comma-separated allowed origins

### Streamlit Cloud Deployment (Frontend)

1. Push your code to GitHub
2. Go to share.streamlit.io
3. Deploy the app pointing to `Task-A/frontend/app.py`
4. Add secrets in the Streamlit dashboard:
   - `API_BASE_URL`: Your deployed backend URL
   - `ADMIN_USERNAME`: Admin username
   - `ADMIN_PASSWORD`: Admin password

---

## Sample cURL Commands

Base URL: `https://predusk-backend-ngpt.onrender.com`

```bash
# Public endpoints
curl -X GET $BASE_URL/health
curl -X GET $BASE_URL/profile
curl -X GET "$BASE_URL/search?q=python"
curl -X GET "$BASE_URL/projects?skill=python&status=completed"
curl -X GET "$BASE_URL/skills/top?limit=5"

# Authenticated endpoints (add -u admin:password)
curl -X POST $BASE_URL/profile -u admin:pass -H "Content-Type: application/json" -d '{"name":"John","email":"john@example.com"}'
curl -X POST $BASE_URL/education -u admin:pass -H "Content-Type: application/json" -d '{"institution":"MIT","degree":"B.S.","field":"CS"}'
curl -X POST $BASE_URL/skills -u admin:pass -H "Content-Type: application/json" -d '{"name":"Python","level":"expert"}'
curl -X DELETE $BASE_URL/profile -u admin:pass
```

---

## Authentication

HTTP Basic Authentication for all write operations (POST, PUT, DELETE).

```bash
curl -u username:password -X POST ...
```

Configure via environment variables: `ADMIN_USERNAME`, `ADMIN_PASSWORD`

---

## Limitations

- **Single Profile** only (no multi-tenancy)
- **Basic Auth** (use HTTPS in production)
- **No Pagination** on list endpoints
- **No File Uploads** for images/PDFs
- **Basic Search** (SQL LIKE, no full-text)
- **No Caching** or rate limiting
- **Synchronous** database operations
- **String Dates** (not proper DATE types)

---

## Future Improvements

- JWT authentication & rate limiting
- Pagination & full-text search
- File uploads & Redis caching

---
