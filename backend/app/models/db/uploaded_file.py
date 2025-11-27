"""
ControlNot v2 - Uploaded File DB Model
Modelo Pydantic para la tabla 'uploaded_files'
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class UploadedFileDB(BaseModel):
    """
    Modelo que representa un archivo subido en la base de datos

    Mapea directamente a la tabla 'uploaded_files'
    Los archivos binarios se almacenan en Supabase Storage
    """

    id: UUID = Field(..., description="UUID del archivo")
    session_id: UUID = Field(..., description="UUID de la sesión de procesamiento")

    # Información del archivo
    filename: str = Field(..., description="Nombre del archivo en storage")
    original_filename: Optional[str] = Field(None, description="Nombre original del archivo")
    category: Optional[str] = Field(
        None,
        description="Categoría: parte_a (deudor), parte_b (banco), otros (inmueble)"
    )

    # Storage
    storage_path: str = Field(..., description="Ruta completa en Supabase Storage")
    storage_bucket: str = Field(default="uploads", description="Bucket de Supabase Storage")

    # Metadata del archivo
    file_hash: Optional[str] = Field(None, description="SHA-256 hash para deduplicación")
    content_type: Optional[str] = Field(None, description="MIME type del archivo")
    size_bytes: Optional[int] = Field(None, description="Tamaño en bytes", ge=0)

    # OCR
    ocr_completed: bool = Field(default=False, description="Si se completó el OCR")
    ocr_text: Optional[str] = Field(None, description="Texto extraído por OCR")
    ocr_confidence: Optional[float] = Field(
        None,
        description="Confianza del OCR (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    # Timestamps
    uploaded_at: datetime = Field(..., description="Fecha de carga")
    processed_at: Optional[datetime] = Field(None, description="Fecha de procesamiento OCR")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "aa0e8400-e29b-41d4-a716-446655440000",
                "session_id": "880e8400-e29b-41d4-a716-446655440000",
                "filename": "INE_frente.pdf",
                "original_filename": "Identificación Cliente.pdf",
                "category": "parte_a",
                "storage_path": "660e8400/880e8400/aa0e8400_INE_frente.pdf",
                "storage_bucket": "uploads",
                "file_hash": "a7b3c9d2e1f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4",
                "content_type": "application/pdf",
                "size_bytes": 1024000,
                "ocr_completed": True,
                "ocr_confidence": 0.98
            }
        }
