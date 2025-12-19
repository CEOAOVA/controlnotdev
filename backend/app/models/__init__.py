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
from app.models.cancelacion import CancelacionKeys

# Identificaciones mexicanas
from app.models.ine import INECredencial
from app.models.pasaporte import PasaporteMexicano
from app.models.curp_constancia import ConstanciaCURP

__all__ = [
    # Documentos notariales
    "BaseKeys",
    "CompraventaKeys",
    "DonacionKeys",
    "TestamentoKeys",
    "PoderKeys",
    "SociedadKeys",
    "CancelacionKeys",
    # Identificaciones mexicanas
    "INECredencial",
    "PasaporteMexicano",
    "ConstanciaCURP",
]