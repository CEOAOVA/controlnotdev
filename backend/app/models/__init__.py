"""
ControlNot v2 - Models Package
Modelos Pydantic para todos los tipos de documentos notariales
"""
from app.models.base import BaseKeys
from app.models.compraventa import CompraventaKeys
from app.models.donacion import DonacionKeys
from app.models.testamento import TestamentoKeys
from app.models.poder import PoderKeys
from app.models.sociedad import SociedadKeys

__all__ = [
    "BaseKeys",
    "CompraventaKeys",
    "DonacionKeys",
    "TestamentoKeys",
    "PoderKeys",
    "SociedadKeys",
]