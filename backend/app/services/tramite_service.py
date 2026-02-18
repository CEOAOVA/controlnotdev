"""
ControlNot v2 - Tramite Service
Lógica de negocio para trámites gubernamentales con semáforo
"""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
import structlog

from app.repositories.case_tramite_repository import case_tramite_repository
from app.repositories.case_activity_repository import case_activity_repository

logger = structlog.get_logger()


def compute_semaforo(tramite: Dict) -> str:
    """
    Calcula el semáforo de un trámite basado en fecha_limite.

    - verde: >5 días restantes
    - amarillo: 1-5 días
    - rojo: <1 día o vencido
    - gris: sin fecha límite o ya completado
    """
    if tramite.get('status') in ('completado', 'cancelado'):
        return 'gris'

    fecha_limite = tramite.get('fecha_limite')
    if not fecha_limite:
        return 'gris'

    if isinstance(fecha_limite, str):
        try:
            fecha_limite = datetime.fromisoformat(fecha_limite.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return 'gris'

    now = datetime.now(timezone.utc)
    diff = (fecha_limite - now).total_seconds() / 86400  # días

    if diff < 1:
        return 'rojo'
    elif diff <= 5:
        return 'amarillo'
    else:
        return 'verde'


class TramiteService:
    """
    Servicio para gestionar trámites con semáforo de vencimiento.
    """

    async def create(
        self,
        tenant_id: UUID,
        case_id: UUID,
        tipo: str,
        nombre: str,
        assigned_to: Optional[UUID] = None,
        fecha_limite: Optional[str] = None,
        costo: Optional[float] = None,
        depende_de: Optional[UUID] = None,
        notas: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """Crea un trámite y registra actividad"""
        tramite = await case_tramite_repository.create_tramite(
            tenant_id=tenant_id,
            case_id=case_id,
            tipo=tipo,
            nombre=nombre,
            assigned_to=assigned_to,
            fecha_limite=fecha_limite,
            costo=costo,
            depende_de=depende_de,
            notas=notas,
        )

        if tramite:
            await case_activity_repository.log(
                tenant_id=tenant_id,
                case_id=case_id,
                action='create_tramite',
                description=f"Trámite creado: {nombre} ({tipo})",
                user_id=user_id,
                entity_type='tramite',
                entity_id=UUID(tramite['id']),
            )

        return tramite

    async def complete(
        self,
        tramite_id: UUID,
        tenant_id: UUID,
        case_id: UUID,
        resultado: Optional[str] = None,
        costo: Optional[float] = None,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """Marca un trámite como completado y registra actividad"""
        tramite = await case_tramite_repository.get_by_id(tramite_id)
        if not tramite:
            raise ValueError("Trámite no encontrado")

        updated = await case_tramite_repository.complete_tramite(
            tramite_id=tramite_id,
            resultado=resultado,
            costo=costo,
        )

        await case_activity_repository.log(
            tenant_id=tenant_id,
            case_id=case_id,
            action='complete_tramite',
            description=f"Trámite completado: {tramite['nombre']}. Resultado: {resultado or 'N/A'}",
            user_id=user_id,
            entity_type='tramite',
            entity_id=tramite_id,
            old_value={'status': tramite['status']},
            new_value={'status': 'completado', 'resultado': resultado},
        )

        return updated

    def get_semaforo(self, tramites: List[Dict]) -> Dict[str, int]:
        """Calcula resumen de semáforo para una lista de trámites"""
        summary = {'verde': 0, 'amarillo': 0, 'rojo': 0, 'gris': 0, 'total': len(tramites)}
        for t in tramites:
            color = compute_semaforo(t)
            summary[color] = summary.get(color, 0) + 1
        return summary

    async def get_overdue(self, tenant_id: UUID) -> List[Dict]:
        """Lista trámites vencidos del tenant"""
        tramites = await case_tramite_repository.list_overdue(tenant_id)
        for t in tramites:
            t['semaforo'] = compute_semaforo(t)
        return tramites

    async def get_upcoming(self, tenant_id: UUID, days: int = 7) -> List[Dict]:
        """Lista trámites próximos a vencer"""
        tramites = await case_tramite_repository.list_upcoming(tenant_id, days=days)
        for t in tramites:
            t['semaforo'] = compute_semaforo(t)
        return tramites

    def enrich_with_semaforo(self, tramites: List[Dict]) -> List[Dict]:
        """Agrega campo semáforo a cada trámite"""
        for t in tramites:
            t['semaforo'] = compute_semaforo(t)
        return tramites


# Instancia singleton
tramite_service = TramiteService()
