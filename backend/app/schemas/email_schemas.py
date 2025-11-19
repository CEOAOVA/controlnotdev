"""
ControlNot v2 - Email Schemas
Schemas para envío de emails con adjuntos

Integra con EmailService para enviar documentos generados
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class EmailRequest(BaseModel):
    """
    Solicitud para enviar email con documento adjunto

    Example:
        {
            "to_email": "cliente@example.com",
            "subject": "Escritura de Compraventa - Lote 145",
            "body": "Estimado cliente, adjunto encontrará su escritura.",
            "document_id": "doc_abc123"
        }
    """
    to_email: EmailStr = Field(
        ...,
        description="Email del destinatario (validado)"
    )
    subject: str = Field(
        ...,
        description="Asunto del email",
        min_length=1,
        max_length=200
    )
    body: str = Field(
        ...,
        description="Cuerpo del mensaje",
        min_length=1,
        max_length=5000
    )
    document_id: str = Field(
        ...,
        description="ID del documento generado a adjuntar"
    )
    html: bool = Field(
        default=False,
        description="Si True, el body se trata como HTML"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "to_email": "cliente@example.com",
                    "subject": "Escritura de Compraventa - Lote 145",
                    "body": "Estimado cliente,\n\nAdjunto encontrará su escritura de compraventa del Lote 145.\n\nSaludos cordiales.",
                    "document_id": "doc_abc123",
                    "html": False
                }
            ]
        }
    }


class EmailResponse(BaseModel):
    """
    Respuesta del envío de email

    Example:
        {
            "success": true,
            "message": "Email enviado exitosamente a cliente@example.com",
            "to_email": "cliente@example.com",
            "document_filename": "Compraventa_Lote_145.docx"
        }
    """
    success: bool = Field(..., description="Si el email se envió exitosamente")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    to_email: str = Field(..., description="Email del destinatario")
    document_filename: Optional[str] = Field(
        None,
        description="Nombre del documento adjunto"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Email enviado exitosamente a cliente@example.com",
                    "to_email": "cliente@example.com",
                    "document_filename": "Compraventa_Lote_145.docx"
                }
            ]
        }
    }
