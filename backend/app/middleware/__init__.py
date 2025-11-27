"""
ControlNot v2 - Middleware Package
Middlewares personalizados para la aplicación
"""
from app.middleware.audit import audit_middleware

__all__ = ['audit_middleware']
