# 🚀 Quick Start Guide

Get the Me-API Playground up and running in 5 minutes!

## Option 1: Docker Compose (Easiest)

```bash
# 1. Clone and enter directory
git clone <your-repo>
cd me-api-playground

# 2. Start everything
docker-compose up -d

# 3. Initialize database
docker-compose exec backend python seed.py

# 4. Access applications
# Frontend: http://localhost:8501
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+

### Backend Setup

```bash
# 1. Create database
createdb me_api_db

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Initialize and seed database
python seed.py

# 5. Run backend
python main.py
# Running at http://localhost:8000
```

### Frontend Setup (New Terminal)

```bash
# 1. Setup frontend
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
export API_BASE_URL=http://localhost:8000

# 3. Run frontend
streamlit run app.py
# Running at http://localhost:8501
```

## Customize Your Data

Edit `backend/seed.py` to add your information:

```python
# Update your profile
profile = Profile(
    name="YOUR NAME",
    email="your.email@example.com",
    # ... add your info
)

# Add your education, work experience, projects, skills
```

Then re-run:
```bash
python backend/seed.py
```

## Test the API

```bash
# Make test script executable
chmod +x test-api.sh

# Run tests
./test-api.sh
```

## Next Steps

1. ✅ Update seed data with your information
2. ✅ Test all endpoints with the API docs at http://localhost:8000/docs
3. ✅ Customize the frontend styling in `frontend/app.py`
4. ✅ Deploy to production (see README.md for deployment guides)

## Common Issues

### Database Connection Failed
```bash
# Check if PostgreSQL is running
pg_isadmin

# Restart PostgreSQL
brew services restart postgresql  # macOS
sudo systemctl restart postgresql  # Linux
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Need Help?

- 📚 Full documentation: See README.md
- 🐛 Report issues: Open a GitHub issue
- 💬 Questions: Check the FAQ in README.md

---

**Happy coding! 🎉**
