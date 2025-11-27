"""
ControlNot v2 - Case Repository
Repositorio para gestión de casos/expedientes notariales
"""
from typing import Dict, List, Optional
from uuid import UUID
import structlog
from postgrest.exceptions import APIError

from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class CaseRepository(BaseRepository):
    """
    Repositorio para la tabla 'cases'

    Gestiona expedientes/trámites notariales vinculados a clientes
    """

    def __init__(self):
        super().__init__('cases')

    async def create_case(
        self,
        tenant_id: UUID,
        client_id: UUID,
        case_number: str,
        document_type: str,
        description: Optional[str] = None,
        parties: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Crea un nuevo caso/expediente

        Args:
            tenant_id: UUID de la notaría
            client_id: UUID del cliente principal
            case_number: Número de expediente (ej: "EXP-CANC-2024-042")
            document_type: Tipo de documento (compraventa, donacion, etc.)
            description: Descripción del caso
            parties: Lista de partes involucradas [{"role": "vendedor", "client_id": "uuid"}]
            metadata: Metadata adicional (JSONB)

        Returns:
            Caso creado
        """
        case_data = {
            'tenant_id': str(tenant_id),
            'client_id': str(client_id),
            'case_number': case_number.upper(),
            'document_type': document_type,
            'status': 'draft',
            'parties': parties or [],
            'metadata': metadata or {}
        }

        if description:
            case_data['description'] = description

        try:
            return await self.create(case_data)

        except APIError as e:
            # Manejar violación de número de caso duplicado
            if 'unique_case_number_per_tenant' in str(e):
                logger.warning(
                    "case_number_duplicate",
                    tenant_id=str(tenant_id),
                    case_number=case_number
                )
                raise ValueError(f"Ya existe un caso con el número {case_number}")
            raise

    async def get_case_with_client(
        self,
        case_id: UUID
    ) -> Optional[Dict]:
        """
        Obtiene un caso con información del cliente vinculado

        Args:
            case_id: UUID del caso

        Returns:
            Caso con datos del cliente
        """
        try:
            result = self._table()\
                .select('*, clients(*)')\
                .eq('id', str(case_id))\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):
                return None
            logger.error("case_get_with_client_failed", case_id=str(case_id), error=str(e))
            raise

    async def get_by_case_number(
        self,
        tenant_id: UUID,
        case_number: str
    ) -> Optional[Dict]:
        """
        Obtiene un caso por su número de expediente

        Args:
            tenant_id: UUID de la notaría
            case_number: Número de expediente

        Returns:
            Caso encontrado o None
        """
        try:
            result = self._table()\
                .select('*')\
                .eq('tenant_id', str(tenant_id))\
                .eq('case_number', case_number.upper())\
                .single()\
                .execute()

            return result.data if result.data else None

        except APIError as e:
            if 'PGRST116' in str(e):
                return None
            logger.error("case_get_by_number_failed", case_number=case_number, error=str(e))
            raise

    async def list_by_client(
        self,
        client_id: UUID,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Lista casos de un cliente específico

        Args:
            client_id: UUID del cliente
            status: Filtrar por estado (opcional)
            limit: Número máximo de resultados

        Returns:
            Lista de casos del cliente
        """
        try:
            query = self._table()\
                .select('*')\
                .eq('client_id', str(client_id))

            if status:
                query = query.eq('status', status)

            result = query\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except APIError as e:
            logger.error("case_list_by_client_failed", client_id=str(client_id), error=str(e))
            raise

    async def list_by_status(
        self,
        tenant_id: UUID,
        status: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Lista casos por estado

        Args:
            tenant_id: UUID de la notaría
            status: Estado a filtrar (draft, documents_uploaded, etc.)
            limit: Número máximo de resultados
            offset: Offset para paginación

        Returns:
            Lista de casos con ese estado
        """
        return await self.list_by_tenant(
            tenant_id=tenant_id,
            filters={'status': status},
            limit=limit,
            offset=offset,
            order_by='created_at',
            descending=True
        )

    async def list_by_document_type(
        self,
        tenant_id: UUID,
        document_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Lista casos por tipo de documento

        Args:
            tenant_id: UUID de la notaría
            document_type: Tipo de documento (compraventa, cancelacion, etc.)
            limit: Número máximo de resultados
            offset: Offset para paginación

        Returns:
            Lista de casos de ese tipo
        """
        return await self.list_by_tenant(
            tenant_id=tenant_id,
            filters={'document_type': document_type},
            limit=limit,
            offset=offset,
            order_by='created_at',
            descending=True
        )

    async def update_status(
        self,
        case_id: UUID,
        new_status: str
    ) -> Optional[Dict]:
        """
        Actualiza el estado de un caso

        Args:
            case_id: UUID del caso
            new_status: Nuevo estado

        Returns:
            Caso actualizado
        """
        updates = {'status': new_status}

        # Si el estado es 'completed', marcar la fecha de completado
        if new_status == 'completed':
            from datetime import datetime, timezone
            updates['completed_at'] = datetime.now(timezone.utc).isoformat()

        return await self.update(case_id, updates)

    async def add_party(
        self,
        case_id: UUID,
        party: Dict
    ) -> Optional[Dict]:
        """
        Agrega una parte involucrada al caso

        Args:
            case_id: UUID del caso
            party: Diccionario con datos de la parte {"role": "...", "client_id": "..."}

        Returns:
            Caso actualizado
        """
        try:
            # Obtener caso actual
            case = await self.get_by_id(case_id)

            if not case:
                return None

            # Agregar nueva parte al array
            parties = case.get('parties', [])
            parties.append(party)

            # Actualizar
            return await self.update(case_id, {'parties': parties})

        except Exception as e:
            logger.error("case_add_party_failed", case_id=str(case_id), error=str(e))
            raise

    async def get_case_statistics(
        self,
        tenant_id: UUID
    ) -> Dict:
        """
        Obtiene estadísticas de casos de una notaría

        Args:
            tenant_id: UUID de la notaría

        Returns:
            Diccionario con estadísticas
        """
        try:
            # Total de casos
            total = await self.count_by_tenant(tenant_id)

            # Por estado
            stats_by_status = {}
            statuses = ['draft', 'documents_uploaded', 'ocr_processing', 'data_extracted',
                       'validated', 'document_generated', 'signed', 'completed', 'cancelled']

            for status in statuses:
                count = await self.count_by_tenant(tenant_id, {'status': status})
                stats_by_status[status] = count

            # Por tipo de documento
            stats_by_type = {}
            doc_types = ['compraventa', 'donacion', 'testamento', 'poder', 'sociedad', 'cancelacion']

            for doc_type in doc_types:
                count = await self.count_by_tenant(tenant_id, {'document_type': doc_type})
                stats_by_type[doc_type] = count

            return {
                'total_cases': total,
                'by_status': stats_by_status,
                'by_document_type': stats_by_type
            }

        except Exception as e:
            logger.error("case_statistics_failed", tenant_id=str(tenant_id), error=str(e))
            raise


# Instancia singleton del repositorio
case_repository = CaseRepository()
