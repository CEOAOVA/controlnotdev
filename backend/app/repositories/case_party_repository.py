"""
ControlNot v2 - Case Party Repository
Repositorio para gestión de partes involucradas en casos/expedientes
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CasePartyRepository(BaseRepository):
    """
    Repositorio para la tabla 'case_parties'

    Gestiona las partes involucradas (vendedor, comprador, donador, etc.)
    """

    def __init__(self):
        super().__init__('case_parties')

    async def list_by_case(
        self,
        case_id: UUID,
        limit: int = 50
    ) -> List[Dict]:
        """Lista partes de un caso ordenadas por orden"""
        try:
            result = self._table()\
                .select('*')\
                .eq('case_id', str(case_id))\
                .order('orden', desc=False)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except APIError as e:
            logger.error("case_parties_list_failed", case_id=str(case_id), error=str(e))
            raise

    async def create_party(
        self,
        tenant_id: UUID,
        case_id: UUID,
        role: str,
        nombre: str,
        client_id: Optional[UUID] = None,
        rfc: Optional[str] = None,
        tipo_persona: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        representante_legal: Optional[str] = None,
        poder_notarial: Optional[str] = None,
        orden: int = 0
    ) -> Optional[Dict]:
        """Crea una nueva parte para un caso"""
        data = {
            'tenant_id': str(tenant_id),
            'case_id': str(case_id),
            'role': role,
            'nombre': nombre,
            'orden': orden,
        }
        if client_id:
            data['client_id'] = str(client_id)
        if rfc:
            data['rfc'] = rfc
        if tipo_persona:
            data['tipo_persona'] = tipo_persona
        if email:
            data['email'] = email
        if telefono:
            data['telefono'] = telefono
        if representante_legal:
            data['representante_legal'] = representante_legal
        if poder_notarial:
            data['poder_notarial'] = poder_notarial

        try:
            return await self.create(data)
        except APIError as e:
            if 'duplicate' in str(e).lower() or '23505' in str(e):
                raise ValueError(f"Ya existe una parte con rol '{role}' para este cliente en el caso")
            raise

    async def update_party(
        self,
        party_id: UUID,
        updates: Dict
    ) -> Optional[Dict]:
        """Actualiza una parte"""
        return await self.update(party_id, updates)

    async def delete_party(self, party_id: UUID) -> bool:
        """Elimina una parte"""
        return await self.delete(party_id)

    async def count_by_case(self, case_id: UUID) -> int:
        """Cuenta partes de un caso"""
        try:
            result = self._table()\
                .select('id', count='exact')\
                .eq('case_id', str(case_id))\
                .execute()
            return result.count if result.count is not None else 0
        except APIError as e:
            logger.error("case_parties_count_failed", case_id=str(case_id), error=str(e))
            raise


# Instancia singleton
case_party_repository = CasePartyRepository()
