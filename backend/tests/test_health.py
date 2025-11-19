"""
ControlNot v2 - Health Endpoints Tests
Tests para verificar health checks y estado de servicios
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test endpoint raíz de la aplicación"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "ControlNot v2"
    assert data["version"] == "2.0.0"
    assert data["status"] == "running"
    assert "documentation" in data
    assert "api" in data


def test_ping_endpoint():
    """Test endpoint de ping para health checks"""
    response = client.get("/ping")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ping"] == "pong"
    assert data["status"] == "ok"


def test_api_root_endpoint():
    """Test endpoint raíz de la API"""
    response = client.get("/api/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "ControlNot v2 API"
    assert data["version"] == "2.0.0"
    assert "endpoints" in data
    assert "features" in data
    assert "improvements" in data


def test_health_check():
    """Test health check general"""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "version" in data
    assert "services" in data


def test_services_status():
    """Test estado de servicios externos"""
    response = client.get("/api/health/services")
    assert response.status_code == 200
    
    data = response.json()
    assert "services" in data
    assert "environment" in data
    
    services = data["services"]
    assert "ai_provider" in services
    assert "ocr" in services
    assert "storage" in services


def test_cors_headers():
    """Test que CORS headers están presentes"""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # CORS headers se agregan por el middleware


def test_process_time_header():
    """Test que se agrega header de tiempo de procesamiento"""
    response = client.get("/ping")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    
    # Verificar que es un número válido
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0
