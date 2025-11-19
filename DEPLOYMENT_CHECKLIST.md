# ControlNot v2 - Deployment Checklist

**Version:** 2.0.0
**Date:** _________________
**Deployed By:** _________________

---

## ✅ Pre-Deployment Checklist

### 1. Server Infrastructure

- [ ] **Server provisioned** (Ubuntu 20.04+ / 2 cores / 4GB RAM / 20GB SSD)
- [ ] **Public IP assigned**
- [ ] **DNS configured** (if using domain name)
- [ ] **Firewall rules set** (ports 80, 443 open)
- [ ] **SSH access configured** and tested
- [ ] **Non-root user created** with sudo privileges

### 2. Software Dependencies

- [ ] **Docker installed** (v20.10+)
  ```bash
  docker --version
  ```
- [ ] **Docker Compose installed** (v2.0+)
  ```bash
  docker-compose --version
  ```
- [ ] **Git installed**
  ```bash
  git --version
  ```
- [ ] **User added to docker group**
  ```bash
  groups $USER | grep docker
  ```

### 3. API Keys & Credentials

- [ ] **OpenAI API Key** obtained (if using OpenAI)
  - Source: https://platform.openai.com/api-keys
  - Validated: _______________

- [ ] **OpenRouter API Key** obtained (recommended)
  - Source: https://openrouter.ai/keys
  - Validated: _______________
  - Credits available: $__________

- [ ] **Google Cloud Vision credentials** created
  - Project ID: _______________
  - Service Account: _______________
  - Vision API enabled: ✅
  - JSON credentials downloaded: ✅

- [ ] **Gmail SMTP configured**
  - Gmail account: _______________
  - App Password generated: ✅
  - 2FA enabled: ✅

- [ ] **Google Drive Folder ID** (optional)
  - Folder ID: _______________

### 4. Repository & Code

- [ ] **Repository cloned**
  ```bash
  git clone <repo-url> /opt/controlnot-v2
  ```
- [ ] **Correct branch checked out**
  - Branch: _______________
  - Commit: _______________

- [ ] **`.env` files configured**
  - `backend/.env` created from `.env.example`
  - All API keys added
  - `FROM_EMAIL` = `SMTP_USER`
  - `GOOGLE_CREDENTIALS_JSON` is one-line JSON
  - File permissions set to 600

- [ ] **Templates available**
  - Templates in `backend/templates/` directory
  - At least one .docx template uploaded

---

## 🚀 Deployment Checklist

### 5. Docker Build

- [ ] **Images built successfully**
  ```bash
  docker-compose build
  ```
  - Backend image: ✅
  - Frontend image: ✅
  - No build errors: ✅

- [ ] **Environment variables loaded**
  ```bash
  docker-compose config | grep -i "api_key"
  ```

### 6. Service Startup

- [ ] **Services started**
  ```bash
  docker-compose up -d
  ```
  - Backend container running: ✅
  - Frontend container running: ✅

- [ ] **Container health checks passed**
  ```bash
  docker-compose ps
  ```
  - `controlnot-backend`: healthy
  - `controlnot-frontend`: healthy

- [ ] **Logs reviewed**
  ```bash
  docker-compose logs -f
  ```
  - No critical errors: ✅
  - All services initialized: ✅

---

## 🧪 Post-Deployment Testing

### 7. Health Checks

- [ ] **Backend health endpoint**
  ```bash
  curl http://localhost:8000/api/health
  ```
  Response: `{"status":"healthy",...}`

- [ ] **Services health endpoint**
  ```bash
  curl http://localhost:8000/api/health/services
  ```
  - OpenAI/OpenRouter: healthy
  - Google Vision: healthy
  - SMTP: healthy

- [ ] **API documentation accessible**
  - URL: http://localhost:8000/docs
  - Swagger UI loads: ✅
  - All endpoints visible: ✅

- [ ] **Frontend accessible**
  - URL: http://localhost:3000
  - Page loads: ✅
  - No console errors: ✅

### 8. Functional Testing

- [ ] **Template upload tested**
  - Template uploads successfully: ✅
  - Placeholders extracted: ✅

- [ ] **Categorized upload tested**
  - Can upload to Parte A: ✅
  - Can upload to Parte B: ✅
  - Can upload to Otros: ✅
  - File validation works: ✅

- [ ] **OCR processing tested**
  - 5-10 images processed: ✅
  - Processing time < 15s: ✅
  - Text extracted correctly: ✅

- [ ] **AI extraction tested**
  - Fields extracted: _____ / _____
  - Confidence score: _____%
  - Key fields populated: ✅

- [ ] **Data editor tested**
  - All fields editable: ✅
  - Search works: ✅
  - Validation works: ✅

- [ ] **Document generation tested**
  - Word document generated: ✅
  - Placeholders replaced: ✅
  - Download works: ✅
  - Document opens in Word: ✅

- [ ] **Email sending tested**
  - Email sent successfully: ✅
  - Document attached: ✅
  - Email received: ✅
  - Attachment opens: ✅

### 9. Performance Testing

- [ ] **Response times acceptable**
  - Health check: < 100ms
  - OCR (10 images): < 15s
  - AI extraction: < 10s
  - Document generation: < 5s

- [ ] **Resource usage acceptable**
  ```bash
  docker stats
  ```
  - Backend CPU: < 50%
  - Backend Memory: < 1GB
  - Frontend Memory: < 200MB

### 10. Security Verification

- [ ] **Environment files secured**
  ```bash
  ls -la backend/.env
  ```
  Permissions: `-rw------- (600)`

- [ ] **Secrets not in git**
  ```bash
  git status
  ```
  `.env` not tracked: ✅

- [ ] **HTTPS configured** (production only)
  - SSL certificate installed: ✅
  - Redirect HTTP → HTTPS: ✅

- [ ] **Firewall rules active**
  ```bash
  sudo ufw status
  ```
  - Port 22 (SSH): allowed
  - Port 80 (HTTP): allowed
  - Port 443 (HTTPS): allowed
  - Other ports: denied

---

## 📊 Monitoring Setup

### 11. Logging Configuration

- [ ] **Log aggregation configured**
  - Logs accessible via `docker-compose logs`
  - Log rotation configured
  - Log retention policy: _____ days

- [ ] **Error alerting configured**
  - Email alerts: _______________
  - Slack webhook: _______________

### 12. Backup Strategy

- [ ] **Backup schedule defined**
  - Frequency: _______________
  - Retention: _______________

- [ ] **Backup tested**
  - Manual backup executed: ✅
  - Restore tested: ✅

---

## 🔄 Rollback Plan

### 13. Rollback Preparation

- [ ] **Previous version tagged**
  - Tag: _______________
  - Commit: _______________

- [ ] **Rollback procedure documented**
  - Steps documented: ✅
  - Tested in staging: ✅

- [ ] **Data backup created**
  - Backup file: _______________
  - Location: _______________
  - Size: _______________

---

## ✅ Go-Live Approval

### Sign-Off

**Deployment Completed:**
- Date: _______________
- Time: _______________
- Deployed By: _______________

**Verification:**
- Technical Lead: _______________
- QA Approved: _______________
- Product Owner: _______________

**Notes:**
_____________________________________________________
_____________________________________________________
_____________________________________________________

---

## 📞 Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| DevOps | __________ | __________ |
| Backend Dev | __________ | __________ |
| Frontend Dev | __________ | __________ |
| Product Owner | __________ | __________ |

---

## 📚 References

- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Testing Guide**: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)

---

**Version:** 2.0.0
**Last Updated:** 2025-01-16
