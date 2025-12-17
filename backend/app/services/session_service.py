"""
ControlNot v2 - Session Management Service
Centralizes all session state management to avoid circular dependencies

This service manages:
- Template sessions (from templates.py)
- Document sessions (from documents.py)
- Extraction results (from extraction.py)
- Cancelación sessions (from cancelaciones.py)

SEGURIDAD: Usa claves compuestas {tenant_id}:{session_id} para aislamiento multi-tenant.
Future: Will be replaced with database persistence via session_repository
"""
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import structlog
from threading import Lock

logger = structlog.get_logger()


def _make_composite_key(tenant_id: Optional[str], session_id: str) -> str:
    """
    Crea clave compuesta para aislamiento multi-tenant

    SEGURIDAD: Si tenant_id está presente, crea clave aislada.
    Si no hay tenant_id (legacy), usa solo session_id.

    Args:
        tenant_id: UUID del tenant (opcional para retrocompatibilidad)
        session_id: ID de la sesión/documento

    Returns:
        Clave compuesta en formato "tenant_id:session_id" o "session_id"
    """
    if tenant_id:
        return f"{tenant_id}:{session_id}"
    return session_id


class SessionManager:
    """
    Centralized session manager for all endpoint session data

    Thread-safe singleton pattern with automatic cleanup
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Storage dictionaries
        self._template_sessions: Dict[str, Dict[str, Any]] = {}
        self._document_sessions: Dict[str, Dict[str, Any]] = {}
        self._extraction_results: Dict[str, Dict[str, Any]] = {}
        self._cancelacion_sessions: Dict[str, Dict[str, Any]] = {}
        self._generated_documents: Dict[str, Dict[str, Any]] = {}

        # Session metadata (for TTL and cleanup)
        self._session_metadata: Dict[str, Dict[str, Any]] = {}

        # Default TTL: 24 hours
        self._default_ttl = timedelta(hours=24)

        self._initialized = True
        logger.info("session_manager_initialized")

    # ==========================================
    # TEMPLATE SESSIONS
    # ==========================================

    def store_template_session(
        self,
        template_id: str,
        data: Dict[str, Any],
        ttl: Optional[timedelta] = None
    ) -> None:
        """
        Store template processing session

        Args:
            template_id: Unique template identifier
            data: Template session data (content, placeholders, etc.)
            ttl: Time-to-live for this session
        """
        with self._lock:
            self._template_sessions[template_id] = data
            self._set_metadata(template_id, "template", ttl)
            logger.debug("template_session_stored", template_id=template_id)

    def get_template_session(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template session data"""
        self._check_expired(template_id)
        return self._template_sessions.get(template_id)

    def delete_template_session(self, template_id: str) -> None:
        """Delete template session"""
        with self._lock:
            self._template_sessions.pop(template_id, None)
            self._session_metadata.pop(template_id, None)
            logger.debug("template_session_deleted", template_id=template_id)

    def list_template_sessions(self) -> Dict[str, Dict[str, Any]]:
        """List all template sessions"""
        self._cleanup_expired()
        return self._template_sessions.copy()

    # ==========================================
    # DOCUMENT SESSIONS
    # ==========================================

    def store_document_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: Optional[timedelta] = None
    ) -> None:
        """
        Store document processing session

        Args:
            session_id: Unique session identifier
            data: Document session data (files, metadata, etc.)
            ttl: Time-to-live for this session
        """
        with self._lock:
            self._document_sessions[session_id] = data
            self._set_metadata(session_id, "document", ttl)
            logger.debug("document_session_stored", session_id=session_id)

    def get_document_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get document session data"""
        self._check_expired(session_id)
        return self._document_sessions.get(session_id)

    def delete_document_session(self, session_id: str) -> None:
        """Delete document session"""
        with self._lock:
            self._document_sessions.pop(session_id, None)
            self._session_metadata.pop(session_id, None)
            logger.debug("document_session_deleted", session_id=session_id)

    # ==========================================
    # EXTRACTION RESULTS
    # ==========================================

    def store_extraction_result(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: Optional[timedelta] = None
    ) -> None:
        """
        Store OCR/AI extraction results

        Args:
            session_id: Unique session identifier
            data: Extraction results data
            ttl: Time-to-live for this session
        """
        with self._lock:
            self._extraction_results[session_id] = data
            self._set_metadata(session_id, "extraction", ttl)
            logger.debug("extraction_result_stored", session_id=session_id)

    def get_extraction_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction result data"""
        self._check_expired(session_id)
        return self._extraction_results.get(session_id)

    def delete_extraction_result(self, session_id: str) -> None:
        """Delete extraction result"""
        with self._lock:
            self._extraction_results.pop(session_id, None)
            self._session_metadata.pop(session_id, None)
            logger.debug("extraction_result_deleted", session_id=session_id)

    # ==========================================
    # CANCELACIÓN SESSIONS
    # ==========================================

    def store_cancelacion_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: Optional[timedelta] = None
    ) -> None:
        """
        Store cancelación processing session

        Args:
            session_id: Unique session identifier
            data: Cancelación session data
            ttl: Time-to-live for this session
        """
        with self._lock:
            self._cancelacion_sessions[session_id] = data
            self._set_metadata(session_id, "cancelacion", ttl)
            logger.debug("cancelacion_session_stored", session_id=session_id)

    def get_cancelacion_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cancelación session data"""
        self._check_expired(session_id)
        return self._cancelacion_sessions.get(session_id)

    def delete_cancelacion_session(self, session_id: str) -> None:
        """Delete cancelación session"""
        with self._lock:
            self._cancelacion_sessions.pop(session_id, None)
            self._session_metadata.pop(session_id, None)
            logger.debug("cancelacion_session_deleted", session_id=session_id)

    # ==========================================
    # GENERATED DOCUMENTS (con aislamiento multi-tenant)
    # ==========================================

    def store_generated_document(
        self,
        doc_id: str,
        data: Dict[str, Any],
        ttl: Optional[timedelta] = None,
        tenant_id: Optional[str] = None
    ) -> None:
        """
        Store generated document content

        SEGURIDAD: Si se proporciona tenant_id, usa clave compuesta para aislamiento.

        Args:
            doc_id: Unique document identifier
            data: Document data (content, filename, stats, etc.)
            ttl: Time-to-live for this document
            tenant_id: UUID del tenant para aislamiento (recomendado)
        """
        key = _make_composite_key(tenant_id, doc_id)
        with self._lock:
            # Guardar tenant_id en data para validación posterior
            if tenant_id:
                data['_tenant_id'] = tenant_id
            self._generated_documents[key] = data
            self._set_metadata(key, "generated_doc", ttl or timedelta(hours=48))
            logger.debug(
                "generated_document_stored",
                doc_id=doc_id,
                tenant_id=tenant_id,
                key=key
            )

    def get_generated_document(
        self,
        doc_id: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get generated document data

        SEGURIDAD: Si se proporciona tenant_id, busca con clave compuesta.
        Valida que el documento pertenezca al tenant.

        Args:
            doc_id: ID del documento
            tenant_id: UUID del tenant (recomendado para seguridad)

        Returns:
            Document data o None si no existe o no pertenece al tenant
        """
        key = _make_composite_key(tenant_id, doc_id)
        self._check_expired(key)
        doc = self._generated_documents.get(key)

        # Si no se encontró con clave compuesta, intentar con solo doc_id (legacy)
        if doc is None and tenant_id:
            doc = self._generated_documents.get(doc_id)
            # Si existe sin tenant_id, validar que no pertenezca a otro tenant
            if doc and doc.get('_tenant_id') and doc['_tenant_id'] != tenant_id:
                logger.warning(
                    "generated_document_access_denied",
                    doc_id=doc_id,
                    requested_tenant=tenant_id,
                    owner_tenant=doc.get('_tenant_id')
                )
                return None

        return doc

    def delete_generated_document(
        self,
        doc_id: str,
        tenant_id: Optional[str] = None
    ) -> None:
        """Delete generated document"""
        key = _make_composite_key(tenant_id, doc_id)
        with self._lock:
            self._generated_documents.pop(key, None)
            self._session_metadata.pop(key, None)
            # También intentar con clave legacy si existe
            if tenant_id:
                self._generated_documents.pop(doc_id, None)
                self._session_metadata.pop(doc_id, None)
            logger.debug("generated_document_deleted", doc_id=doc_id, tenant_id=tenant_id)

    # ==========================================
    # UTILITY METHODS
    # ==========================================

    def _set_metadata(
        self,
        session_id: str,
        session_type: str,
        ttl: Optional[timedelta] = None
    ) -> None:
        """Set session metadata for TTL tracking"""
        self._session_metadata[session_id] = {
            "type": session_type,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + (ttl or self._default_ttl)
        }

    def _check_expired(self, session_id: str) -> None:
        """Check if session has expired and delete if so"""
        metadata = self._session_metadata.get(session_id)
        if metadata and datetime.now() > metadata["expires_at"]:
            with self._lock:
                # Delete from appropriate storage
                session_type = metadata["type"]
                if session_type == "template":
                    self._template_sessions.pop(session_id, None)
                elif session_type == "document":
                    self._document_sessions.pop(session_id, None)
                elif session_type == "extraction":
                    self._extraction_results.pop(session_id, None)
                elif session_type == "cancelacion":
                    self._cancelacion_sessions.pop(session_id, None)
                elif session_type == "generated_doc":
                    self._generated_documents.pop(session_id, None)

                self._session_metadata.pop(session_id, None)
                logger.info("session_expired_and_deleted", session_id=session_id, type=session_type)

    def _cleanup_expired(self) -> int:
        """
        Clean up all expired sessions

        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            now = datetime.now()
            expired_sessions = [
                session_id
                for session_id, metadata in self._session_metadata.items()
                if now > metadata["expires_at"]
            ]

            for session_id in expired_sessions:
                self._check_expired(session_id)

            if expired_sessions:
                logger.info("expired_sessions_cleaned", count=len(expired_sessions))

            return len(expired_sessions)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get session manager statistics

        Returns:
            Statistics about active sessions
        """
        self._cleanup_expired()

        return {
            "template_sessions": len(self._template_sessions),
            "document_sessions": len(self._document_sessions),
            "extraction_results": len(self._extraction_results),
            "cancelacion_sessions": len(self._cancelacion_sessions),
            "generated_documents": len(self._generated_documents),
            "total_sessions": len(self._session_metadata)
        }

    def clear_all(self) -> None:
        """
        Clear all sessions (use with caution!)

        This is mainly for testing purposes
        """
        with self._lock:
            self._template_sessions.clear()
            self._document_sessions.clear()
            self._extraction_results.clear()
            self._cancelacion_sessions.clear()
            self._generated_documents.clear()
            self._session_metadata.clear()
            logger.warning("all_sessions_cleared")


# Global singleton instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """
    Get the global SessionManager instance

    Returns:
        SessionManager: Global session manager
    """
    return _session_manager
