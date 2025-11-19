"""
ControlNot v2 - Documents Endpoints Tests
Tests para verificar categorización y generación de documentos
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)


def test_get_categories():
    """Test obtener categorías disponibles para documentos"""
    response = client.get("/api/documents/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert "total" in data
    
    # Verificar que hay exactamente 3 categorías
    assert data["total"] == 3
    assert len(data["categories"]) == 3
    
    # Verificar categorías específicas
    category_ids = [c["id"] for c in data["categories"]]
    expected = ["parte_a", "parte_b", "otros"]
    for expected_cat in expected:
        assert expected_cat in category_ids
    
    # Verificar estructura de categoría
    parte_a = next(c for c in data["categories"] if c["id"] == "parte_a")
    assert "name" in parte_a
    assert "description" in parte_a
    assert parte_a["name"] == "Parte A"


def test_upload_documents_missing_template():
    """Test upload de documentos sin template_id"""
    files = {
        "parte_a": [("test1.pdf", BytesIO(b"fake pdf"), "application/pdf")]
    }
    form_data = {
        "document_type": "compraventa"
        # template_id faltante
    }
    
    response = client.post("/api/documents/upload", data=form_data, files=files)
    assert response.status_code == 422  # Validation error


def test_upload_documents_invalid_type():
    """Test upload con tipo de documento inválido"""
    files = {
        "parte_a": [("test1.pdf", BytesIO(b"fake pdf"), "application/pdf")]
    }
    form_data = {
        "document_type": "invalid_type",
        "template_id": "tpl_test123"
    }
    
    response = client.post("/api/documents/upload", data=form_data, files=files)
    assert response.status_code == 422  # Validation error


def test_upload_documents_no_files():
    """Test upload sin archivos"""
    form_data = {
        "document_type": "compraventa",
        "template_id": "tpl_test123"
    }
    
    response = client.post("/api/documents/upload", data=form_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data


def test_generate_document_not_found():
    """Test generar documento con template que no existe"""
    request_data = {
        "template_id": "tpl_nonexistent",
        "responses": {"key1": "value1"},
        "placeholders": ["key1"],
        "output_filename": "test_output.docx"
    }
    
    response = client.post("/api/documents/generate", json=request_data)
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


def test_generate_document_invalid_filename():
    """Test generar documento con nombre de archivo inválido"""
    request_data = {
        "template_id": "tpl_test123",
        "responses": {"key1": "value1"},
        "placeholders": ["key1"],
        "output_filename": ""  # Nombre vacío
    }
    
    response = client.post("/api/documents/generate", json=request_data)
    assert response.status_code == 422  # Validation error


def test_download_document_not_found():
    """Test descargar documento que no existe"""
    response = client.get("/api/documents/download/nonexistent_id")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


def test_generate_document_missing_placeholders():
    """Test generar documento sin placeholders"""
    request_data = {
        "template_id": "tpl_test123",
        "responses": {"key1": "value1"},
        "placeholders": [],  # Lista vacía
        "output_filename": "test.docx"
    }
    
    response = client.post("/api/documents/generate", json=request_data)
    assert response.status_code == 422  # Validation error (min_length=1)
