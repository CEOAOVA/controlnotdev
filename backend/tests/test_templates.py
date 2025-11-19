"""
ControlNot v2 - Templates Endpoints Tests
Tests para verificar upload y procesamiento de templates
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)


def test_list_template_types():
    """Test listado de tipos de template disponibles"""
    response = client.get("/api/templates/types")
    assert response.status_code == 200
    
    data = response.json()
    assert "types" in data
    assert "total" in data
    
    # Verificar que hay exactamente 5 tipos
    assert data["total"] == 5
    assert len(data["types"]) == 5
    
    # Verificar tipos específicos
    type_ids = [t["id"] for t in data["types"]]
    expected = ["compraventa", "donacion", "testamento", "poder", "sociedad"]
    for expected_type in expected:
        assert expected_type in type_ids


def test_upload_template_invalid_extension():
    """Test upload con extensión inválida"""
    # Crear un archivo falso con extensión .txt
    file_content = b"Not a docx file"
    files = {
        "file": ("test.txt", BytesIO(file_content), "text/plain")
    }
    
    response = client.post("/api/templates/upload", files=files)
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "docx" in data["detail"].lower()


def test_upload_template_empty_file():
    """Test upload con archivo vacío"""
    # Crear un archivo vacío con extensión .docx
    file_content = b""
    files = {
        "file": ("test.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    
    response = client.post("/api/templates/upload", files=files)
    # Puede fallar por diferentes razones (archivo vacío, no válido, etc)
    # Lo importante es que no retorne 200
    assert response.status_code != 200


def test_confirm_template_not_found():
    """Test confirmar template que no existe"""
    request_data = {
        "template_id": "tpl_nonexistent",
        "document_type": "compraventa",
        "confirmed": True
    }
    
    response = client.post("/api/templates/confirm", json=request_data)
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


def test_confirm_template_not_confirmed():
    """Test confirmar sin el flag confirmed=true"""
    request_data = {
        "template_id": "tpl_test123",
        "document_type": "compraventa",
        "confirmed": False
    }
    
    response = client.post("/api/templates/confirm", json=request_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "true" in data["detail"].lower()


def test_list_templates_empty():
    """Test listar templates cuando no hay ninguno"""
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    
    data = response.json()
    assert "templates" in data
    assert "total" in data
    assert isinstance(data["templates"], list)
    assert data["total"] == len(data["templates"])
