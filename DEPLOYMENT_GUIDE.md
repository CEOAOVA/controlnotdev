# ControlNot v2 - Deployment Guide

**Version:** 2.0.0
**Last Updated:** 2025-01-16
**Target Platform:** VPS (Ubuntu 20.04+), Docker Compose

---

## 📋 Table of Contents

1. [Pre-requisites](#pre-requisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Post-Deployment Testing](#post-deployment-testing)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)
7. [Monitoring & Logs](#monitoring--logs)

---

## 1. Pre-requisites

### Server Requirements

**Minimum Specifications:**
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 20GB SSD
- **OS:** Ubuntu 20.04 LTS or higher
- **Network:** Public IP with ports 80, 443, 3000, 8000 available

**Software Required:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- curl/wget
- Optional: nginx/Traefik for reverse proxy

### Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### API Keys & Credentials

Before deployment, you'll need:

1. **OpenAI API Key** OR **OpenRouter API Key**
   - OpenAI: https://platform.openai.com/api-keys
   - OpenRouter: https://openrouter.ai/keys
   - Recommended: OpenRouter (multi-provider support)

2. **Google Cloud Vision API Credentials**
   - Create project: https://console.cloud.google.com
   - Enable Vision API
   - Create Service Account
   - Download JSON credentials

3. **Gmail SMTP Credentials**
   - Gmail account
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Note: Regular password won't work, must use App Password

4. **Google Drive Folder ID** (Optional)
   - For template storage
   - Get folder ID from Drive URL

---

## 2. Environment Setup

### Clone Repository

```bash
# Clone project
cd /opt
git clone <your-repo-url> controlnot-v2
cd controlnot-v2
```

### Configure Backend Environment

```bash
cd backend
cp .env.example .env
nano .env
```

**Complete `.env` file:**

```bash
# ==================================
# CONTROLNOT V2 - ENVIRONMENT CONFIG
# ==================================

# OpenAI (Fallback directo)
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE

# OpenRouter (Multi-provider - Recommended)
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
OPENROUTER_MODEL=openai/gpt-4o
# Other models: anthropic/claude-3.5-sonnet, google/gemini-pro-1.5

# Google Cloud Vision (OCR)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id","private_key_id":"xxx","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"your-service-account@your-project.iam.gserviceaccount.com","client_id":"xxx","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"xxx"}

# Google Drive (optional - for templates)
GOOGLE_DRIVE_FOLDER_ID=

# Email (SMTP Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com

# App Config
APP_URL=http://your-domain.com
```

**Important Notes:**
- ⚠️ `GOOGLE_CREDENTIALS_JSON` must be **one line**, no newlines
- ⚠️ Use Gmail **App Password**, not regular password
- ⚠️ `FROM_EMAIL` should match `SMTP_USER`
- ⚠️ Keep this file secure, never commit to git

### Configure Frontend Environment (Optional)

```bash
cd ../frontend
cp .env.example .env
nano .env
```

```bash
VITE_API_URL=http://localhost:8000
```

---

## 3. Docker Deployment

### Build and Start Services

```bash
# From project root
cd /opt/controlnot-v2

# Build images
docker-compose build

# Start services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Verify Services

```bash
# Check running containers
docker-compose ps

# Should show:
# controlnot-backend   Up   0.0.0.0:8000->8000/tcp
# controlnot-frontend  Up   0.0.0.0:3000->80/tcp
```

### Access Application

- **Frontend**: http://your-server-ip:3000
- **Backend API**: http://your-server-ip:8000
- **API Docs**: http://your-server-ip:8000/docs

---

## 4. Post-Deployment Testing

### Health Check

```bash
# Test backend health
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","version":"2.0.0","timestamp":"..."}
```

### Test Services

```bash
# Test with detailed service health
curl http://localhost:8000/api/health/services

# Should return status of:
# - OpenAI/OpenRouter connection
# - Google Vision API
# - SMTP email service
```

### End-to-End Test

1. **Access Frontend**: http://your-server-ip:3000
2. **Select Template**: Choose "Compraventa" or upload custom .docx
3. **Upload Images**:
   - Parte A: 2-3 images (seller documents)
   - Parte B: 2-3 images (buyer documents)
   - Otros: 1-2 images (property documents)
4. **Process**: Click "Procesar Documentos"
5. **Verify**:
   - OCR completes in ~10s (for 5-10 images)
   - AI extraction shows extracted fields
   - Data editor displays 40-50 fields
   - Edit any field if needed
6. **Generate**: Click "Generar Documento"
7. **Download**: Verify Word document downloads
8. **Email Test**: Send document to test email, verify receipt

---

## 5. Troubleshooting

### Backend Won't Start

**Symptom:** `controlnot-backend` container exits immediately

**Check logs:**
```bash
docker-compose logs backend
```

**Common Issues:**

1. **Invalid Google Credentials**
   ```
   Error: Failed to initialize Vision client
   ```
   **Fix:** Verify `GOOGLE_CREDENTIALS_JSON` is valid JSON on one line

2. **Missing API Keys**
   ```
   Error: OPENAI_API_KEY or OPENROUTER_API_KEY required
   ```
   **Fix:** Add at least one AI provider API key to `.env`

3. **SMTP Connection Failed**
   ```
   Error: SMTP authentication failed
   ```
   **Fix:**
   - Use Gmail App Password (not regular password)
   - Enable "Less secure app access" if needed
   - Verify `SMTP_USER` and `FROM_EMAIL` match

4. **Port Already in Use**
   ```
   Error: Bind for 0.0.0.0:8000 failed: port is already allocated
   ```
   **Fix:**
   ```bash
   # Find process using port
   sudo lsof -i :8000
   # Kill process or change port in docker-compose.yml
   ```

### Frontend Connection Error

**Symptom:** Frontend shows "Cannot connect to backend"

**Checks:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/api/health
   ```
2. Check nginx proxy configuration in `frontend/nginx.conf`
3. Verify CORS settings in backend
4. Check browser console for errors

### OCR Not Working

**Symptom:** "OCR failed" error during processing

**Checks:**
1. **Verify Vision API is enabled**:
   - Go to Google Cloud Console
   - Check Vision API is enabled for your project

2. **Check Credentials**:
   ```bash
   # Inside backend container
   docker-compose exec backend python -c "from app.core.dependencies import initialize_vision_client; client = initialize_vision_client(); print('Vision client OK')"
   ```

3. **Check API Quota**:
   - Go to Google Cloud Console → APIs & Services → Quotas
   - Verify you haven't exceeded free tier limits

### AI Extraction Fails

**Symptom:** "AI extraction failed" after OCR completes

**Checks:**
1. **Verify API Key**:
   ```bash
   # Test OpenRouter
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"

   # Or test OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

2. **Check API Credits**:
   - OpenRouter: https://openrouter.ai/activity
   - OpenAI: https://platform.openai.com/usage

3. **Check Logs**:
   ```bash
   docker-compose logs backend | grep "AI extraction"
   ```

### Email Sending Fails

**Symptom:** "Email failed to send" error

**Checks:**
1. **Verify SMTP Settings**:
   ```bash
   # Test SMTP connection
   docker-compose exec backend python -c "
   from app.services.email_service import EmailService
   from app.core.config import settings
   service = EmailService()
   print('SMTP config:', settings.SMTP_SERVER, settings.SMTP_PORT)
   "
   ```

2. **Test Send**:
   ```bash
   # Send test email
   curl -X POST http://localhost:8000/api/documents/send-email \
     -H "Content-Type: application/json" \
     -d '{
       "to_email": "test@example.com",
       "subject": "Test",
       "body": "Test email",
       "document_id": "test_doc"
     }'
   ```

3. **Gmail Specific**:
   - Use App Password (not regular password)
   - Enable 2FA on Gmail account first
   - Generate App Password: https://myaccount.google.com/apppasswords

---

## 6. Rollback Procedures

### Quick Rollback

```bash
# Stop current version
docker-compose down

# Pull previous working version
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Data Preservation

```bash
# Backup volumes before rollback
docker run --rm -v controlnot-v2_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .

# Restore after rollback
docker run --rm -v controlnot-v2_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /data
```

### Database Migration Rollback

If you've migrated from JSON to database:

```bash
# Revert to JSON storage
docker-compose down
git checkout <commit-before-db-migration>
docker-compose build
docker-compose up -d
```

---

## 7. Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since specific time
docker-compose logs --since="2025-01-16T10:00:00" backend
```

### Log Files

Logs are also saved to:
- Backend: `backend/logs/app.log` (inside container)
- Frontend: nginx access/error logs

### Performance Monitoring

```bash
# Container stats
docker stats

# Detailed backend metrics
curl http://localhost:8000/api/health/services
```

### Disk Usage

```bash
# Check Docker disk usage
docker system df

# Clean up old images/containers
docker system prune -a
```

---

## 8. Security Best Practices

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Use Reverse Proxy (nginx/Traefik)

Recommended for production to handle SSL/TLS:

```bash
# Install nginx
sudo apt install nginx

# Configure reverse proxy for port 3000 → 80/443
# See: nginx-example.conf in docs/
```

### Environment Security

```bash
# Restrict .env file permissions
chmod 600 backend/.env

# Never commit .env to git
git rm --cached backend/.env  # if accidentally added
```

### Regular Updates

```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
```

---

## 9. Scaling Considerations

### Horizontal Scaling

For high traffic, deploy multiple backend replicas:

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

### Load Balancer

Add nginx/traefik in front:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### Database Migration

For production at scale, migrate from JSON to PostgreSQL/Supabase:

1. Setup PostgreSQL
2. Update `storage_service.py` to use SQLAlchemy
3. Run migrations
4. Update docker-compose.yml to include PostgreSQL

---

## 10. Support & Resources

### Documentation
- Quick Start: [QUICK_START.md](QUICK_START.md)
- API Reference: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Testing Guide: [TESTING_GUIDE.md](TESTING_GUIDE.md)

### Health Endpoints
- Basic: `GET /api/health`
- Services: `GET /api/health/services`

### Logs Location
- Backend: `docker-compose logs backend`
- Frontend: `docker-compose logs frontend`

### Common Commands
```bash
# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Stop all services
docker-compose down

# Stop and remove volumes (DESTRUCTIVE)
docker-compose down -v
```

---

**Version:** 2.0.0
**Maintainer:** ControlNot Team
**Last Reviewed:** 2025-01-16
