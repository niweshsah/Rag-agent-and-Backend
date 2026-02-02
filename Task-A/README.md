# 🚀 Me-API Playground

A production-ready, live queryable resume/portfolio built with FastAPI, PostgreSQL, and Streamlit. This project acts as both a traditional portfolio and an interactive API that showcases your professional experience, projects, and skills.

![Architecture](https://img.shields.io/badge/Architecture-Clean-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Local Development](#-local-development)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Contributing](#-contributing)

## ✨ Features

### Backend API
- ✅ **RESTful API** with automatic OpenAPI documentation
- ✅ **Full CRUD operations** on profile data
- ✅ **Advanced filtering** for projects by skill and status
- ✅ **Global search** across projects and work experience
- ✅ **Skill analytics** with project count aggregation
- ✅ **Basic Authentication** for protected endpoints
- ✅ **CORS configuration** for cross-origin requests
- ✅ **Error handling** for 404 and 500 errors
- ✅ **Health checks** for monitoring

### Frontend UI
- ✅ **Interactive dashboard** with real-time data
- ✅ **Search functionality** with live results
- ✅ **Project filtering** by skills and status
- ✅ **Skills visualization** with interactive charts
- ✅ **Responsive design** with custom styling
- ✅ **Multiple pages** for different content types

### Database
- ✅ **Normalized schema** with proper relationships
- ✅ **SQLAlchemy ORM** for type-safe queries
- ✅ **Automatic migrations** with Alembic support
- ✅ **Seed data** for quick setup

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Streamlit Frontend (Port 8501)                  │
│  - Profile Dashboard                                         │
│  - Project Portfolio                                         │
│  - Skills Analytics                                          │
│  - Search Interface                                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8000)                    │
│  Routes:                                                     │
│  • GET  /health          - Health check                      │
│  • GET  /profile         - Get full profile                  │
│  • PUT  /profile         - Update profile (Auth)             │
│  • GET  /projects        - List/filter projects              │
│  • GET  /skills/top      - Get top skills                    │
│  • GET  /search          - Global search                     │
└────────────────────────┬────────────────────────────────────┘
                         │ SQLAlchemy ORM
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            PostgreSQL Database (Port 5432)                   │
│  Tables:                                                     │
│  • profiles           • education                            │
│  • work_experience    • projects                             │
│  • skills             • social_links                         │
│  • project_skills (junction table)                           │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.109.0
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0.25
- **Server:** Uvicorn with async support
- **Authentication:** HTTP Basic Auth
- **Validation:** Pydantic v2

### Frontend
- **Framework:** Streamlit 1.29.0
- **HTTP Client:** Requests
- **Visualization:** Plotly Express
- **Data Processing:** Pandas

### DevOps
- **Containerization:** Docker & Docker Compose
- **Deployment:** Render, Railway, or Fly.io
- **Database Hosting:** Render PostgreSQL (Free tier)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- Docker & Docker Compose (optional, recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd me-api-playground

# Start all services
docker-compose up -d

# Initialize database and seed data
docker-compose exec backend python seed.py

# Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

```bash
# 1. Setup PostgreSQL
createdb me_api_db

# 2. Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python seed.py

# Run backend
python main.py
# Backend running at http://localhost:8000

# 3. Setup Frontend (in new terminal)
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
export API_BASE_URL=http://localhost:8000
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=changeme123

# Run frontend
streamlit run app.py
# Frontend running at http://localhost:8501
```

## 💻 Local Development

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (when implemented)
pytest

# Format code
black .
isort .
```

### Frontend Development

```bash
cd frontend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py --server.port 8501

# Streamlit will auto-reload on file changes
```

### Database Management

```bash
# Access PostgreSQL CLI
psql me_api_db

# Reset database
dropdb me_api_db
createdb me_api_db
python backend/seed.py

# Backup database
pg_dump me_api_db > backup.sql

# Restore database
psql me_api_db < backup.sql
```

## 📚 API Documentation

### Base URL
- **Development:** `http://localhost:8000`
- **Production:** `https://your-app.onrender.com`

### Endpoints

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

#### Get Profile
```bash
GET /profile

Response:
{
  "id": 1,
  "name": "Your Name",
  "email": "your.email@example.com",
  "phone": "+1 (555) 123-4567",
  "location": "San Francisco, CA",
  "bio": "Full-Stack Engineer...",
  "education": [...],
  "work_experience": [...],
  "projects": [...],
  "skills": [...],
  "social_links": [...]
}
```

#### Update Profile (Requires Auth)
```bash
PUT /profile
Authorization: Basic base64(username:password)
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "new.email@example.com",
  "bio": "Updated bio...",
  "skills": [
    {
      "name": "Python",
      "level": "expert",
      "category": "backend",
      "years_experience": 5.0
    }
  ]
}
```

#### Get Projects (with filters)
```bash
# All projects
GET /projects

# Filter by skill
GET /projects?skill=React

# Filter by status
GET /projects?status=completed

# Combine filters
GET /projects?skill=Python&status=in-progress
```

#### Get Top Skills
```bash
GET /skills/top?limit=10

Response:
[
  {
    "id": 1,
    "name": "React",
    "level": "expert",
    "category": "frontend",
    "years_experience": 4.0,
    "project_count": 5
  },
  ...
]
```

#### Search
```bash
GET /search?q=microservices

Response:
[
  {
    "type": "project",
    "id": 1,
    "title": "E-Commerce Platform",
    "description": "Built with microservices architecture...",
    "relevance_score": 1.5
  },
  ...
]
```

### Authentication

Protected endpoints require HTTP Basic Authentication:

```bash
# Using curl
curl -X PUT http://localhost:8000/profile \
  -u admin:changeme123 \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name", "email": "new@example.com"}'

# Using Python requests
import requests
from requests.auth import HTTPBasicAuth

response = requests.put(
    "http://localhost:8000/profile",
    auth=HTTPBasicAuth("admin", "changeme123"),
    json={"name": "New Name", "email": "new@example.com"}
)
```

### Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🌐 Deployment

### Deploy to Render (Recommended)

#### 1. Backend Deployment

```bash
# Create render.yaml in project root
cat > render.yaml << 'EOF'
services:
  - type: web
    name: me-api-backend
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && python seed.py && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: me-api-db
          property: connectionString
      - key: ADMIN_USERNAME
        value: admin
      - key: ADMIN_PASSWORD
        generateValue: true
      - key: ALLOWED_ORIGINS
        value: https://your-frontend.streamlit.app

databases:
  - name: me-api-db
    databaseName: me_api_db
    user: postgres
EOF

# Deploy to Render
# 1. Push to GitHub
# 2. Connect repository to Render
# 3. Render will auto-deploy using render.yaml
```

#### 2. Frontend Deployment (Streamlit Cloud)

```bash
# 1. Push code to GitHub
# 2. Go to https://share.streamlit.io
# 3. Connect repository
# 4. Set environment variables in Streamlit Cloud:
#    - API_BASE_URL: https://your-backend.onrender.com
#    - ADMIN_USERNAME: admin
#    - ADMIN_PASSWORD: your-password
# 5. Deploy
```

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up

# Add PostgreSQL
railway add --plugin postgresql
```

### Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy backend
cd backend
fly launch --name me-api-backend
fly deploy

# Deploy database
fly postgres create --name me-api-db

# Deploy frontend
cd ../frontend
fly launch --name me-api-frontend
fly deploy
```

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here

# CORS
ALLOWED_ORIGINS=http://localhost:8501,https://your-frontend.streamlit.app
```

#### Frontend
```bash
# API Configuration
API_BASE_URL=http://localhost:8000  # or production URL

# Authentication (for admin features)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here
```

### Customizing Seed Data

Edit `backend/seed.py` to update your profile information:

```python
# Update profile
profile = Profile(
    name="Your Name",
    email="your.email@example.com",
    phone="+1 (555) 123-4567",
    location="Your City, State",
    bio="Your professional bio..."
)

# Add your education
education_data = [
    Education(
        institution="Your University",
        degree="Your Degree",
        field="Your Field",
        # ... more fields
    )
]

# Add your work experience
# Add your projects
# Add your skills
```

## 📁 Project Structure

```
me-api-playground/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication logic
│   ├── seed.py              # Database seeding script
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Docker configuration
│   └── .env.example         # Environment template
├── frontend/
│   ├── app.py               # Streamlit application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Docker configuration
├── database/
│   └── (migrations and backups)
├── docker-compose.yml       # Multi-container setup
├── ARCHITECTURE.md          # System architecture docs
└── README.md                # This file
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v

# Run with coverage
pytest --cov=. tests/

# Run specific test
pytest tests/test_api.py::test_get_profile
```

### API Testing with curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test profile endpoint
curl http://localhost:8000/profile | jq

# Test search
curl "http://localhost:8000/search?q=react" | jq

# Test authenticated endpoint
curl -u admin:changeme123 -X PUT \
  http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "test@example.com"}'
```

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Backend: Follow PEP 8, use `black` and `isort`
- Frontend: Follow PEP 8 for Python code
- Write descriptive commit messages
- Add docstrings to functions and classes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- Streamlit for rapid frontend development
- PostgreSQL for reliable data storage
- The open-source community

## 📧 Contact

**Your Name**
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

**Built with ❤️ using FastAPI, PostgreSQL, and Streamlit**
