# 🌐 Deployment Guide

Complete guide for deploying Me-API Playground to production.

## Table of Contents
- [Render Deployment](#render-deployment-recommended)
- [Streamlit Cloud](#streamlit-cloud-frontend)
- [Railway Deployment](#railway-deployment)
- [Fly.io Deployment](#flyio-deployment)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)

---

## Render Deployment (Recommended)

### Why Render?
- ✅ Free tier includes PostgreSQL
- ✅ Automatic deployments from Git
- ✅ SSL certificates included
- ✅ Easy environment variable management

### Step 1: Prepare Your Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Configure:
   - **Name:** `me-api-db`
   - **Database:** `me_api_db`
   - **User:** `postgres`
   - **Region:** Choose closest to you
   - **Plan:** Free
3. Click "Create Database"
4. **Save the Internal Database URL** (you'll need this)

### Step 4: Deploy Backend

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `me-api-backend`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python seed.py && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

4. Add Environment Variables:
   ```
   DATABASE_URL = [Your Internal Database URL from Step 3]
   ADMIN_USERNAME = admin
   ADMIN_PASSWORD = [Generate a secure password]
   ALLOWED_ORIGINS = *
   PYTHON_VERSION = 3.11
   ```

5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
7. **Save your backend URL:** `https://me-api-backend.onrender.com`

### Step 5: Verify Backend

```bash
# Test health endpoint
curl https://me-api-backend.onrender.com/health

# Test profile endpoint
curl https://me-api-backend.onrender.com/profile

# View API docs
open https://me-api-backend.onrender.com/docs
```

---

## Streamlit Cloud (Frontend)

### Step 1: Prepare Streamlit Configuration

Create `frontend/.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
headless = true
port = 8501
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub repository
4. Configure:
   - **Repository:** Your repo
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`

5. Advanced Settings → Secrets:
   ```toml
   API_BASE_URL = "https://me-api-backend.onrender.com"
   ADMIN_USERNAME = "admin"
   ADMIN_PASSWORD = "your-secure-password"
   ```

6. Click "Deploy!"
7. Your app will be available at: `https://your-app.streamlit.app`

### Step 3: Update CORS

Go back to Render backend environment variables and update:
```
ALLOWED_ORIGINS = https://your-app.streamlit.app
```

Redeploy backend if needed.

---

## Railway Deployment

### Prerequisites
```bash
npm install -g @railway/cli
railway login
```

### Deploy Database

```bash
railway init
railway add --plugin postgresql
```

### Deploy Backend

```bash
cd backend
railway up

# Set environment variables
railway variables set DATABASE_URL=[your-db-url]
railway variables set ADMIN_USERNAME=admin
railway variables set ADMIN_PASSWORD=secure-password
```

### Deploy Frontend

```bash
cd ../frontend
railway up

# Set environment variables
railway variables set API_BASE_URL=[your-backend-url]
```

---

## Fly.io Deployment

### Prerequisites
```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

### Deploy Database

```bash
fly postgres create --name me-api-db --region sjc
fly postgres attach me-api-db
```

### Deploy Backend

```bash
cd backend

# Create fly.toml
cat > fly.toml << 'EOF'
app = "me-api-backend"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
EOF

# Deploy
fly deploy
```

### Deploy Frontend

```bash
cd ../frontend

# Create fly.toml
cat > fly.toml << 'EOF'
app = "me-api-frontend"

[env]
  PORT = "8501"

[http_service]
  internal_port = 8501
  force_https = true
EOF

# Deploy
fly deploy
```

---

## Environment Variables

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ADMIN_USERNAME` | Admin username for auth | `admin` |
| `ADMIN_PASSWORD` | Admin password for auth | `secure_password_123` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://app.streamlit.app` |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `https://api.render.com` |
| `ADMIN_USERNAME` | Admin username (optional) | `admin` |
| `ADMIN_PASSWORD` | Admin password (optional) | `secure_password_123` |

---

## Post-Deployment

### 1. Test Your Deployment

```bash
# Set your production URL
PROD_URL="https://me-api-backend.onrender.com"

# Test health
curl $PROD_URL/health

# Test profile
curl $PROD_URL/profile | jq

# Test search
curl "$PROD_URL/search?q=react" | jq
```

### 2. Update Your README

Add deployment badges:
```markdown
[![Backend](https://img.shields.io/badge/Backend-Live-success)](https://me-api-backend.onrender.com)
[![Frontend](https://img.shields.io/badge/Frontend-Live-success)](https://your-app.streamlit.app)
```

### 3. Monitor Your Application

**Render:**
- View logs: Dashboard → Your Service → Logs
- Monitor metrics: Dashboard → Your Service → Metrics

**Streamlit Cloud:**
- View logs: App → Manage app → Logs
- Monitor usage: App → Analytics

### 4. Set Up Custom Domain (Optional)

**Render:**
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records
4. SSL certificate is automatic

**Streamlit Cloud:**
- Custom domains available on paid plans

### 5. Enable HTTPS

All platforms provide free SSL certificates automatically!

### 6. Database Backups

**Render:**
- Free tier: Manual backups via dashboard
- Paid tier: Automatic daily backups

**Backup Command:**
```bash
# Render (requires CLI)
render db backup create me-api-db

# Manual backup
pg_dump $DATABASE_URL > backup.sql
```

---

## Common Deployment Issues

### Issue: Database Connection Failed

**Solution:**
```bash
# Check DATABASE_URL format
# Should be: postgresql://user:pass@host:5432/dbname

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: CORS Errors

**Solution:**
```bash
# Update ALLOWED_ORIGINS to include frontend URL
# In Render: Settings → Environment → Edit ALLOWED_ORIGINS
# Add: https://your-app.streamlit.app
```

### Issue: Build Failed

**Solution:**
```bash
# Ensure Python version is specified
echo "3.11" > runtime.txt

# Or in environment variables
PYTHON_VERSION=3.11
```

### Issue: Database Not Seeded

**Solution:**
```bash
# SSH into your backend (Render)
render shell me-api-backend

# Run seed script
python seed.py
```

---

## Scaling Considerations

### Free Tier Limitations

**Render:**
- 750 hours/month
- Sleep after 15 min inactivity
- 512 MB RAM

**Streamlit Cloud:**
- 1 GB RAM
- Limited CPU
- Sleeps after inactivity

### Upgrading for Production

Consider upgrading when:
- Users > 100/day
- Response time > 2 seconds
- Need always-on service
- Need more than 512 MB RAM

**Recommended Paid Plans:**
- Render: $7/month (always on, 512 MB)
- Streamlit: $20/month (private apps, more resources)

---

## Security Checklist

- [ ] Use strong admin password
- [ ] Enable HTTPS (automatic)
- [ ] Set CORS to specific origins
- [ ] Keep dependencies updated
- [ ] Monitor error logs
- [ ] Set up rate limiting (production)
- [ ] Use environment variables for secrets
- [ ] Regular database backups

---

## Monitoring & Maintenance

### Health Checks

Set up monitoring with UptimeRobot or similar:
```
URL: https://me-api-backend.onrender.com/health
Interval: 5 minutes
```

### Log Aggregation

For production, consider:
- Sentry for error tracking
- Loggly for log management
- New Relic for performance monitoring

---

**Congratulations! Your Me-API Playground is now live! 🎉**

Need help? Check the main README.md or open an issue.
