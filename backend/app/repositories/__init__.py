"""
ControlNot v2 - Repositorios
Capa de acceso a datos para todas las entidades
"""

from app.repositories.base import BaseRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.uploaded_file_repository import UploadedFileRepository


__all__ = [
    "BaseRepository",
    "ClientRepository",
    "CaseRepository",
    "SessionRepository",
    "DocumentRepository",
    "UploadedFileRepository",
]
