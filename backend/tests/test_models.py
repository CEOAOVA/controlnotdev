"""
ControlNot v2 - Models Endpoints Tests
Tests para verificar listado de modelos AI y tipos de documento
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_ai_models():
    """Test listado de modelos AI disponibles"""
    response = client.get("/api/models")
    assert response.status_code == 200
    
    data = response.json()
    assert "models" in data
    assert "total_models" in data
    assert "using_openrouter" in data
    assert "default_model" in data
    
    # Verificar que hay al menos un modelo
    assert data["total_models"] >= 1
    assert len(data["models"]) >= 1
    
    # Verificar estructura de modelo
    first_model = data["models"][0]
    assert "id" in first_model
    assert "name" in first_model
    assert "provider" in first_model
    assert "supports_json" in first_model
    assert "recommended" in first_model


def test_list_document_types():
    """Test listado de tipos de documento soportados"""
    response = client.get("/api/models/types")
    assert response.status_code == 200
    
    data = response.json()
    assert "document_types" in data
    assert "total_types" in data
    
    # Verificar que hay exactamente 5 tipos
    assert data["total_types"] == 5
    assert len(data["document_types"]) == 5
    
    # Verificar que están los 5 tipos esperados
    type_ids = [dt["id"] for dt in data["document_types"]]
    expected_types = ["compraventa", "donacion", "testamento", "poder", "sociedad"]
    for expected_type in expected_types:
        assert expected_type in type_ids
    
    # Verificar estructura de tipo de documento
    first_type = data["document_types"][0]
    assert "id" in first_type
    assert "name" in first_type
    assert "fields_count" in first_type
    assert "description" in first_type


def test_compraventa_type_details():
    """Test detalles específicos del tipo compraventa"""
    response = client.get("/api/models/types")
    assert response.status_code == 200
    
    data = response.json()
    compraventa = next(
        (dt for dt in data["document_types"] if dt["id"] == "compraventa"),
        None
    )
    
    assert compraventa is not None
    assert compraventa["name"] == "Compraventa"
    assert compraventa["fields_count"] == 42


def test_donacion_type_details():
    """Test detalles específicos del tipo donación"""
    response = client.get("/api/models/types")
    assert response.status_code == 200
    
    data = response.json()
    donacion = next(
        (dt for dt in data["document_types"] if dt["id"] == "donacion"),
        None
    )
    
    assert donacion is not None
    assert donacion["name"] == "Donación"
    assert donacion["fields_count"] == 49  # Con lógica temporal
