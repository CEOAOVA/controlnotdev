FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Google Cloud y psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo
COPY . .

# Puerto FastAPI
EXPOSE 8000

# Comando de inicio con Gunicorn + Uvicorn workers para mejor concurrencia
# - 2 workers para manejar requests concurrentes
# - timeout de 120s para operaciones largas (OCR, AI)
# - graceful timeout de 30s para shutdown limpio
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5"]
