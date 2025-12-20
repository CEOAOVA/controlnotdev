"""
Schemas para el perfil de notaría
Usado para pre-llenar datos del instrumento en la extracción
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotaryProfileResponse(BaseModel):
    """Respuesta con datos del perfil de la notaría"""
    # Datos de la notaría (de tabla tenants)
    nombre: str = Field(..., description="Nombre de la notaría")
    rfc: str = Field(..., description="RFC de la notaría")
    numero_notaria: Optional[int] = Field(None, description="Número de la notaría")
    numero_notaria_palabras: Optional[str] = Field(None, description="Número en palabras (ej: catorce)")
    estado: str = Field(..., description="Estado donde se ubica")
    ciudad: Optional[str] = Field(None, description="Ciudad donde se ubica")
    direccion: Optional[str] = Field(None, description="Dirección completa")

    # Datos del notario titular
    notario_nombre: Optional[str] = Field(None, description="Nombre completo del notario")
    notario_titulo: str = Field("Licenciado", description="Título (Licenciado, Doctor, etc.)")

    # Control de numeración
    ultimo_numero_instrumento: int = Field(0, description="Último número de instrumento usado")

    # Campos calculados para uso en templates
    notario_completo: Optional[str] = Field(None, description="Título + Nombre del notario")
    lugar_instrumento: Optional[str] = Field(None, description="Ciudad, Estado para el instrumento")

    class Config:
        from_attributes = True


class NotaryProfileUpdate(BaseModel):
    """Request para actualizar el perfil de la notaría"""
    # Solo los campos editables
    notario_nombre: Optional[str] = Field(None, description="Nombre completo del notario titular")
    notario_titulo: Optional[str] = Field(None, description="Título del notario")
    numero_notaria: Optional[int] = Field(None, description="Número de la notaría")
    numero_notaria_palabras: Optional[str] = Field(None, description="Número en palabras")
    ciudad: Optional[str] = Field(None, description="Ciudad")
    estado: Optional[str] = Field(None, description="Estado")
    direccion: Optional[str] = Field(None, description="Dirección completa")


class IncrementInstrumentResponse(BaseModel):
    """Respuesta al incrementar número de instrumento"""
    nuevo_numero: int = Field(..., description="Nuevo número de instrumento")
    numero_palabras: str = Field(..., description="Número en palabras")
