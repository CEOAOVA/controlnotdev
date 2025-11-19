# ControlNot V2 - Quick Start Guide

## 📋 Prerequisites

- Docker & Docker Compose installed
- OpenAI API key or OpenRouter API key
- Google Cloud Vision API credentials
- Gmail account with App Password (for email functionality)

## 🚀 Quick Start (5 minutes)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd controlnot-v2
```

### 2. Configure Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit .env and add your credentials
nano backend/.env  # or use your preferred editor
```

**Required variables:**
- `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
- `GOOGLE_CREDENTIALS_JSON` (Google Cloud Vision)
- `SMTP_USER` and `SMTP_PASSWORD` (Gmail)

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Test the Application

1. Open http://localhost:3000
2. Select a template or upload your own .docx file
3. Upload categorized images (Parte A, Parte B, Otros)
4. Click "Procesar Documentos"
5. Review and edit extracted data
6. Download or email the final document

## 🔧 Development Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env file
cp .env.example .env
# Edit .env with your credentials

# Run development server
python -m app.main
```

Access at: http://localhost:8000

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Access at: http://localhost:5173

## 📁 Project Structure

```
controlnot-v2/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration & dependencies
│   │   ├── models/        # Pydantic models (6 document types)
│   │   ├── schemas/       # API schemas
│   │   ├── services/      # Business logic (9 services)
│   │   ├── api/           # REST endpoints (5 routers)
│   │   └── utils/         # Utilities
│   ├── data/              # JSON storage (MVP)
│   ├── templates/         # Word templates
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Pages
│   │   ├── api/           # API client
│   │   ├── hooks/         # Custom hooks
│   │   ├── store/         # Zustand stores
│   │   └── lib/           # Utilities
│   └── Dockerfile
└── docker-compose.yml
```

## 🔑 Key Features

✅ **10x Faster OCR** - Async parallel processing (60s → 6-8s)
✅ **Multi-Provider AI** - OpenRouter (GPT-4o, Claude, Gemini) + OpenAI fallback
✅ **5 Document Types** - Compraventa, Donación, Testamento, Poder, Sociedad
✅ **136 Data Fields** - Comprehensive extraction
✅ **Modern Stack** - React + TypeScript + FastAPI

## 🛠️ Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check health
curl http://localhost:8000/api/health
```

## 🐛 Troubleshooting

### Backend won't start
- Check `.env` file has all required variables
- Verify Google credentials JSON is valid
- Check logs: `docker-compose logs backend`

### Frontend shows connection error
- Ensure backend is running on port 8000
- Check nginx proxy configuration
- Verify CORS settings in backend

### OCR not working
- Validate Google Cloud Vision credentials
- Check quota limits in Google Cloud Console
- Verify images are valid formats (JPG, PNG, PDF)

### AI extraction fails
- Confirm OpenAI/OpenRouter API key is valid
- Check API quota/credits
- Review logs for specific error messages

## 📚 Next Steps

- Read full documentation in `/docs`
- Review API docs at http://localhost:8000/docs
- Check `ARQUITECTURA_VALIDACION.md` for technical details
- See `MVP_PLAN_COMPLETO.md` for feature roadmap

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review error messages in API docs
3. Open an issue on GitHub

---

**Version**: 2.0.0
**Last Updated**: 2025-01-16
