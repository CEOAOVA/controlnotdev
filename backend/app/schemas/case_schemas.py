"""
ControlNot v2 - Case Schemas
Schemas de request/response para endpoints de casos/expedientes
"""
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# ==========================================
# REQUEST SCHEMAS (original)
# ==========================================

class CaseCreateRequest(BaseModel):
    """Request para crear un nuevo caso/expediente"""

    client_id: UUID = Field(..., description="UUID del cliente principal")
    case_number: str = Field(..., min_length=1, description="Número de expediente")
    document_type: str = Field(
        ...,
        description="Tipo: compraventa, donacion, testamento, poder, sociedad, cancelacion"
    )
    description: Optional[str] = Field(None, description="Descripción del caso")
    parties: Optional[List[Dict]] = Field(
        default_factory=list,
        description="Partes involucradas: [{\"role\": \"vendedor\", \"client_id\": \"uuid\"}]"
    )
    metadata: Optional[Dict] = Field(default_factory=dict, description="Metadata adicional")
    # Nuevos campos CRM
    priority: Optional[str] = Field('normal', description="Prioridad: baja, normal, alta, urgente")
    assigned_to: Optional[UUID] = Field(None, description="UUID del usuario asignado")
    valor_operacion: Optional[float] = Field(None, description="Valor de la operación")
    fecha_firma: Optional[datetime] = Field(None, description="Fecha programada de firma")
    notas: Optional[str] = Field(None, description="Notas del caso")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags del caso")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "case_number": "EXP-CANC-2024-042",
                "document_type": "cancelacion",
                "description": "Cancelación de hipoteca BBVA Bancomer - Inmueble en Polanco",
                "priority": "alta",
                "valor_operacion": 2500000.00,
                "parties": [
                    {
                        "role": "deudor",
                        "client_id": "550e8400-e29b-41d4-a716-446655440000",
                        "nombre": "JUAN CARLOS MARTINEZ LOPEZ"
                    }
                ]
            }
        }


class CaseUpdateRequest(BaseModel):
    """Request para actualizar un caso"""

    description: Optional[str] = None
    parties: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    escritura_number: Optional[str] = None
    volumen: Optional[str] = None
    folio_real: Optional[str] = None
    valor_operacion: Optional[float] = None
    fecha_firma: Optional[datetime] = None
    notas: Optional[str] = None
    tags: Optional[List[str]] = None


class CaseUpdateStatusRequest(BaseModel):
    """Request para actualizar el estado de un caso"""

    status: str = Field(
        ...,
        description="Nuevo estado: borrador, en_revision, checklist_pendiente, presupuesto, calculo_impuestos, en_firma, postfirma, tramites_gobierno, inscripcion, facturacion, entrega, cerrado, cancelado"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "en_revision"
            }
        }


class CaseAddPartyRequest(BaseModel):
    """Request para agregar una parte al caso"""

    role: str = Field(..., description="Rol de la parte (vendedor, comprador, testador, etc.)")
    client_id: Optional[UUID] = Field(None, description="UUID del cliente (si existe)")
    nombre: Optional[str] = Field(None, description="Nombre (si no es un cliente registrado)")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Datos adicionales de la parte")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "comprador",
                "client_id": "660e8400-e29b-41d4-a716-446655440000",
                "nombre": "MARIA FERNANDA LOPEZ GARCIA"
            }
        }


# ==========================================
# REQUEST SCHEMAS (CRM nuevos)
# ==========================================

class CaseTransitionRequest(BaseModel):
    """Request para transicionar el status de un caso (state machine)"""

    status: str = Field(..., description="Nuevo status del workflow")
    notes: Optional[str] = Field(None, description="Nota sobre la transición")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "en_revision",
                "notes": "Documentos iniciales revisados"
            }
        }


class CaseSuspendRequest(BaseModel):
    """Request para suspender un caso"""

    reason: str = Field(..., min_length=1, description="Razón de la suspensión")

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Esperando documentación faltante del cliente"
            }
        }


class CasePartyCreateRequest(BaseModel):
    """Request para crear una parte normalizada"""

    role: str = Field(..., description="Rol: vendedor, comprador, donador, donatario, deudor, acreedor, etc.")
    nombre: str = Field(..., min_length=1, description="Nombre completo")
    client_id: Optional[UUID] = Field(None, description="UUID del cliente si existe en el sistema")
    rfc: Optional[str] = Field(None, description="RFC")
    tipo_persona: Optional[str] = Field(None, description="fisica o moral")
    email: Optional[str] = Field(None, description="Email de contacto")
    telefono: Optional[str] = Field(None, description="Teléfono")
    representante_legal: Optional[str] = Field(None, description="Si es persona moral")
    poder_notarial: Optional[str] = Field(None, description="Referencia del poder notarial")
    orden: int = Field(0, description="Orden de display")


class CasePartyUpdateRequest(BaseModel):
    """Request para actualizar una parte"""

    role: Optional[str] = None
    nombre: Optional[str] = None
    rfc: Optional[str] = None
    tipo_persona: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    representante_legal: Optional[str] = None
    poder_notarial: Optional[str] = None
    orden: Optional[int] = None


class ChecklistItemCreateRequest(BaseModel):
    """Request para crear un item de checklist custom"""

    nombre: str = Field(..., description="Nombre del documento requerido")
    categoria: str = Field(..., description="Categoría: parte_a, parte_b, inmueble, fiscal, gobierno, general")
    obligatorio: bool = Field(True, description="Si es obligatorio")
    notas: Optional[str] = Field(None, description="Notas adicionales")


class ChecklistItemUpdateRequest(BaseModel):
    """Request para actualizar status de un item de checklist"""

    status: str = Field(..., description="Status: pendiente, solicitado, recibido, aprobado, rechazado, no_aplica")
    notas: Optional[str] = Field(None, description="Notas")


class ChecklistInitializeRequest(BaseModel):
    """Request para inicializar checklist desde catálogo"""

    document_type: Optional[str] = Field(None, description="Tipo de documento (usa el del caso si no se especifica)")


class TramiteCreateRequest(BaseModel):
    """Request para crear un trámite"""

    tipo: str = Field(..., description="Tipo: pago_impuestos, inscripcion_rpp, aviso_sat, etc.")
    nombre: str = Field(..., description="Nombre legible del trámite")
    assigned_to: Optional[UUID] = Field(None, description="UUID del responsable")
    fecha_limite: Optional[datetime] = Field(None, description="Fecha límite")
    costo: Optional[float] = Field(None, description="Costo estimado")
    depende_de: Optional[UUID] = Field(None, description="UUID del trámite del que depende")
    notas: Optional[str] = Field(None, description="Notas")


class TramiteUpdateRequest(BaseModel):
    """Request para actualizar un trámite"""

    nombre: Optional[str] = None
    assigned_to: Optional[UUID] = None
    status: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    costo: Optional[float] = None
    notas: Optional[str] = None


class TramiteCompleteRequest(BaseModel):
    """Request para completar un trámite"""

    resultado: Optional[str] = Field(None, description="Resultado: folio, número de recibo, etc.")
    costo: Optional[float] = Field(None, description="Costo final")


class CaseNoteRequest(BaseModel):
    """Request para agregar una nota al caso"""

    note: str = Field(..., min_length=1, description="Texto de la nota")


class CatalogoChecklistCreateRequest(BaseModel):
    """Request para crear un template de checklist en el catálogo"""

    document_type: str = Field(..., description="Tipo de documento")
    nombre: str = Field(..., description="Nombre del documento requerido")
    categoria: str = Field(..., description="Categoría: parte_a, parte_b, inmueble, fiscal, gobierno, general")
    obligatorio: bool = Field(True)
    orden: int = Field(0)


class CatalogoChecklistUpdateRequest(BaseModel):
    """Request para actualizar un template de checklist"""

    nombre: Optional[str] = None
    categoria: Optional[str] = None
    obligatorio: Optional[bool] = None
    orden: Optional[int] = None


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class CaseResponse(BaseModel):
    """Response con datos de un caso"""

    id: UUID
    tenant_id: UUID
    client_id: UUID
    case_number: str
    document_type: str
    status: str
    parties: Optional[List[Dict]] = Field(default_factory=list)
    description: Optional[str] = None
    metadata: Optional[Dict] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    # Nuevos campos CRM
    assigned_to: Optional[UUID] = None
    priority: Optional[str] = None
    escritura_number: Optional[str] = None
    volumen: Optional[str] = None
    folio_real: Optional[str] = None
    valor_operacion: Optional[float] = None
    fecha_firma: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    notas: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CaseWithClientResponse(CaseResponse):
    """Response con caso y datos del cliente"""

    client: Optional[Dict] = Field(None, description="Datos del cliente principal")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "case_number": "EXP-CANC-2024-042",
                "document_type": "cancelacion",
                "status": "en_revision",
                "priority": "alta",
                "client": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ",
                    "rfc": "MALJ850315ABC"
                }
            }
        }


class CaseWithSessionsResponse(CaseWithClientResponse):
    """Response con caso, cliente y sesiones"""

    sessions: List[Dict] = Field(default_factory=list, description="Sesiones de procesamiento")
    documents_count: int = Field(0, description="Número de documentos generados")


class CaseDetailResponse(CaseWithClientResponse):
    """Response con caso completo enriquecido: parties, checklist, trámites"""

    case_parties: List[Dict] = Field(default_factory=list, description="Partes normalizadas")
    checklist_summary: Optional[Dict] = Field(None, description="Resumen del checklist")
    tramites_summary: Optional[Dict] = Field(None, description="Resumen de trámites con semáforo")
    available_transitions: List[Dict] = Field(default_factory=list, description="Transiciones disponibles")


class CaseListResponse(BaseModel):
    """Response para lista de casos"""

    cases: List[CaseResponse]
    total: int
    page: int = 1
    page_size: int = 50


class CaseStatisticsResponse(BaseModel):
    """Response con estadísticas de casos"""

    total_cases: int
    by_status: Dict[str, int] = Field(..., description="Casos por estado")
    by_document_type: Dict[str, int] = Field(..., description="Casos por tipo de documento")


class CasePartyResponse(BaseModel):
    """Response con datos de una parte"""

    id: UUID
    tenant_id: UUID
    case_id: UUID
    client_id: Optional[UUID] = None
    role: str
    nombre: str
    rfc: Optional[str] = None
    tipo_persona: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    representante_legal: Optional[str] = None
    poder_notarial: Optional[str] = None
    orden: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChecklistItemResponse(BaseModel):
    """Response con datos de un item de checklist"""

    id: UUID
    tenant_id: UUID
    case_id: UUID
    nombre: str
    categoria: str
    status: str
    obligatorio: bool
    uploaded_file_id: Optional[UUID] = None
    storage_path: Optional[str] = None
    fecha_solicitud: Optional[datetime] = None
    fecha_recepcion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    notas: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TramiteResponse(BaseModel):
    """Response con datos de un trámite"""

    id: UUID
    tenant_id: UUID
    case_id: UUID
    assigned_to: Optional[UUID] = None
    tipo: str
    nombre: str
    status: str
    fecha_inicio: Optional[datetime] = None
    fecha_limite: Optional[datetime] = None
    fecha_completado: Optional[datetime] = None
    resultado: Optional[str] = None
    costo: Optional[float] = None
    depende_de: Optional[UUID] = None
    notas: Optional[str] = None
    semaforo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Join data (optional)
    cases: Optional[Dict] = None

    class Config:
        from_attributes = True


class SemaforoSummary(BaseModel):
    """Resumen de semáforo de trámites"""

    verde: int = 0
    amarillo: int = 0
    rojo: int = 0
    gris: int = 0
    total: int = 0


class CaseTimelineResponse(BaseModel):
    """Response con timeline de actividad de un caso"""

    case_id: UUID
    events: List[Dict] = Field(default_factory=list, description="Eventos de actividad")
    total: int = 0
    limit: int = 50
    offset: int = 0


class CaseDashboardResponse(BaseModel):
    """Response con resumen para dashboard"""

    total_cases: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    semaforo_global: SemaforoSummary
    overdue_tramites: int
    upcoming_tramites: int


class TransitionResponse(BaseModel):
    """Response con transiciones disponibles"""

    current_status: str
    current_label: str
    transitions: List[Dict[str, str]]


class CatalogoChecklistResponse(BaseModel):
    """Response con datos de un template de checklist"""

    id: UUID
    tenant_id: Optional[UUID] = None
    document_type: str
    nombre: str
    categoria: str
    obligatorio: bool
    orden: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
