"""
ControlNot v2 - WhatsApp AI Responder
Suggested replies based on keyword matching (MVP)
"""
from typing import Optional
import structlog

logger = structlog.get_logger()

# Intent patterns: list of (keywords, intent_name, suggested_response)
_INTENT_PATTERNS = [
    # Greetings
    (
        ['hola', 'buenos dias', 'buenas tardes', 'buenas noches', 'buen dia'],
        'greeting',
        'Buen dia! Bienvenido a la notaria. ¿En que le podemos ayudar?',
    ),
    # Status inquiry
    (
        ['estado', 'expediente', 'como va', 'avance', 'status', 'progreso'],
        'status_inquiry',
        'Con gusto le informo sobre el estado de su expediente. ¿Me puede proporcionar su nombre completo o numero de expediente?',
    ),
    # Document requirements
    (
        ['documentos', 'requisitos', 'que necesito', 'que ocupo', 'papeles'],
        'document_requirements',
        'Los documentos necesarios dependen del tipo de tramite. ¿Podria indicarme que tipo de operacion desea realizar?',
    ),
    # Appointment
    (
        ['cita', 'agendar', 'horario', 'cuando puedo', 'disponibilidad'],
        'appointment',
        'Con gusto le agendamos una cita. ¿Que dia y horario le conviene? Nuestro horario es de lunes a viernes, 9:00 a 18:00.',
    ),
    # Cost inquiry
    (
        ['costo', 'precio', 'cuanto', 'presupuesto', 'cobran', 'tarifa'],
        'cost_inquiry',
        'El costo depende del tipo y valor de la operacion. ¿Podria indicarme que tramite desea realizar para darle un presupuesto?',
    ),
    # Thanks
    (
        ['gracias', 'muchas gracias', 'agradezco'],
        'thanks',
        'Con gusto! Si tiene alguna otra duda, no dude en contactarnos.',
    ),
]


class WAAutoResponder:
    """MVP AI responder using keyword matching for common intents"""

    def suggest_reply(self, message_text: str) -> Optional[str]:
        """
        Analyze a client message and suggest a reply.

        Returns suggested text or None if no intent matched.
        """
        if not message_text:
            return None

        text_lower = message_text.lower().strip()

        for keywords, intent, response in _INTENT_PATTERNS:
            for kw in keywords:
                if kw in text_lower:
                    logger.debug("wa_ai_intent_matched", intent=intent, keyword=kw)
                    return response

        return None

    def get_intent(self, message_text: str) -> Optional[str]:
        """Get the detected intent name, or None"""
        if not message_text:
            return None

        text_lower = message_text.lower().strip()
        for keywords, intent, _ in _INTENT_PATTERNS:
            for kw in keywords:
                if kw in text_lower:
                    return intent
        return None


# Singleton
wa_auto_responder = WAAutoResponder()
