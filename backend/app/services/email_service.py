"""
ControlNot v2 - Email Service
Envío de emails con SMTP (sync + async)
MEJORA: Soporte async con aiosmtplib + validación con email-validator

Migrado de por_partes.py líneas 1885-1909
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, List, Dict
import structlog

try:
    import aiosmtplib
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    logger = structlog.get_logger()
    logger.warning("aiosmtplib no instalado, solo modo sync disponible")

from email_validator import validate_email, EmailNotValidError

from app.core.config import settings

logger = structlog.get_logger()


class EmailService:
    """
    Servicio de envío de emails vía SMTP

    Soporte para:
    - Envío sincrónico (smtplib)
    - Envío asíncrono (aiosmtplib)
    - Validación de emails
    - Adjuntos
    - HTML
    - TLS/SSL
    """

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Args:
            smtp_server: Servidor SMTP (default: settings.SMTP_SERVER)
            smtp_port: Puerto SMTP (default: settings.SMTP_PORT)
            smtp_user: Usuario SMTP (default: settings.SMTP_USER)
            smtp_password: Contraseña SMTP (default: settings.SMTP_PASSWORD)
            from_email: Email remitente (default: settings.FROM_EMAIL)
        """
        self.smtp_server = smtp_server or settings.SMTP_SERVER
        self.smtp_port = smtp_port or settings.SMTP_PORT
        self.smtp_user = smtp_user or settings.SMTP_USER
        self.smtp_password = smtp_password or settings.SMTP_PASSWORD
        self.from_email = from_email or settings.FROM_EMAIL

        logger.debug(
            "EmailService inicializado",
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            from_email=self.from_email
        )

    def _validate_email(self, email: str) -> bool:
        """
        Valida formato de email

        Args:
            email: Email a validar

        Returns:
            bool: True si es válido

        Raises:
            EmailNotValidError: Si el email no es válido
        """
        try:
            # Validar con email-validator
            valid = validate_email(email)
            normalized_email = valid.email

            logger.debug(
                "Email validado",
                original=email,
                normalized=normalized_email
            )

            return True

        except EmailNotValidError as e:
            logger.error(
                "Email inválido",
                email=email,
                error=str(e)
            )
            raise

    def _create_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_data: Optional[Dict] = None,
        html: bool = False
    ) -> MIMEMultipart:
        """
        Crea mensaje MIME para envío

        Args:
            to_email: Destinatario
            subject: Asunto
            body: Cuerpo del mensaje
            attachment_data: Dict con 'content' (bytes) y 'filename' (str)
            html: Si True, el body se trata como HTML

        Returns:
            MIMEMultipart: Mensaje listo para enviar
        """
        # Validar emails
        self._validate_email(to_email)
        self._validate_email(self.from_email)

        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Añadir cuerpo
        mime_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, mime_type, 'utf-8'))

        # Añadir adjunto si existe
        if attachment_data:
            attachment_content = attachment_data.get('content')
            attachment_filename = attachment_data.get('filename', 'attachment.bin')

            if attachment_content:
                part = MIMEApplication(attachment_content, Name=attachment_filename)
                part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
                msg.attach(part)

                logger.debug(
                    "Adjunto añadido al mensaje",
                    filename=attachment_filename,
                    size_bytes=len(attachment_content)
                )

        return msg

    def send_email_sync(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_data: Optional[Dict] = None,
        html: bool = False
    ) -> bool:
        """
        Envía email de forma sincrónica

        Args:
            to_email: Destinatario
            subject: Asunto del email
            body: Cuerpo del email
            attachment_data: Dict opcional con adjunto:
                {
                    'content': bytes,
                    'filename': str
                }
            html: Si True, body se envía como HTML

        Returns:
            bool: True si se envió exitosamente

        Example:
            >>> email_service = EmailService()
            >>> success = email_service.send_email_sync(
            ...     'cliente@example.com',
            ...     'Escritura Lista',
            ...     'Su escritura está lista para recoger.',
            ...     attachment_data={
            ...         'content': document_bytes,
            ...         'filename': 'Escritura_001.docx'
            ...     }
            ... )

        Raises:
            Exception: Si falla el envío
        """
        logger.info(
            "Enviando email (sync)",
            to_email=to_email,
            subject=subject,
            has_attachment=attachment_data is not None,
            html=html
        )

        try:
            # Crear mensaje
            msg = self._create_message(to_email, subject, body, attachment_data, html)

            # Conectar a servidor SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Iniciar TLS
                server.login(self.smtp_user, self.smtp_password)

                # Enviar
                server.sendmail(
                    self.from_email,
                    to_email,
                    msg.as_string()
                )

            logger.info(
                "Email enviado exitosamente (sync)",
                to_email=to_email,
                subject=subject
            )

            return True

        except Exception as e:
            logger.error(
                "Error al enviar email (sync)",
                to_email=to_email,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_data: Optional[Dict] = None,
        html: bool = False
    ) -> bool:
        """
        Envía email de forma asíncrona

        Requiere aiosmtplib instalado

        Args:
            to_email: Destinatario
            subject: Asunto
            body: Cuerpo
            attachment_data: Adjunto opcional
            html: Si True, body es HTML

        Returns:
            bool: True si se envió exitosamente

        Raises:
            ImportError: Si aiosmtplib no está instalado
            Exception: Si falla el envío
        """
        if not ASYNC_AVAILABLE:
            raise ImportError(
                "aiosmtplib no instalado. "
                "Instalar con: pip install aiosmtplib"
            )

        logger.info(
            "Enviando email (async)",
            to_email=to_email,
            subject=subject,
            has_attachment=attachment_data is not None,
            html=html
        )

        try:
            # Crear mensaje
            msg = self._create_message(to_email, subject, body, attachment_data, html)

            # Enviar con aiosmtplib
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            logger.info(
                "Email enviado exitosamente (async)",
                to_email=to_email,
                subject=subject
            )

            return True

        except Exception as e:
            logger.error(
                "Error al enviar email (async)",
                to_email=to_email,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def send_bulk_emails_sync(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict[str, List[str]]:
        """
        Envía el mismo email a múltiples destinatarios (sync)

        Args:
            recipients: Lista de emails destinatarios
            subject: Asunto
            body: Cuerpo
            html: Si True, body es HTML

        Returns:
            Dict: Resultados:
                {
                    'success': ['email1@...', ...],
                    'failed': ['email2@...', ...]
                }
        """
        results = {
            'success': [],
            'failed': []
        }

        for recipient in recipients:
            try:
                self.send_email_sync(recipient, subject, body, html=html)
                results['success'].append(recipient)
            except Exception as e:
                logger.error(
                    "Error en envío bulk",
                    recipient=recipient,
                    error=str(e)
                )
                results['failed'].append(recipient)

        logger.info(
            "Envío bulk completado",
            total=len(recipients),
            success=len(results['success']),
            failed=len(results['failed'])
        )

        return results

    async def send_bulk_emails_async(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict[str, List[str]]:
        """
        Envía el mismo email a múltiples destinatarios (async)

        Args:
            recipients: Lista de emails destinatarios
            subject: Asunto
            body: Cuerpo
            html: Si True, body es HTML

        Returns:
            Dict: Resultados con 'success' y 'failed'
        """
        import asyncio

        results = {
            'success': [],
            'failed': []
        }

        async def send_one(recipient: str):
            try:
                await self.send_email_async(recipient, subject, body, html=html)
                results['success'].append(recipient)
            except Exception as e:
                logger.error(
                    "Error en envío bulk async",
                    recipient=recipient,
                    error=str(e)
                )
                results['failed'].append(recipient)

        # Enviar todos en paralelo
        tasks = [send_one(recipient) for recipient in recipients]
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(
            "Envío bulk async completado",
            total=len(recipients),
            success=len(results['success']),
            failed=len(results['failed'])
        )

        return results


def send_email_smtp(
    to_email: str,
    subject: str,
    body: str,
    attachment_data: Optional[Dict] = None,
    html: bool = False
) -> bool:
    """
    Función pública para enviar email (versión sync)

    Wrapper sobre EmailService.send_email_sync()

    Args:
        to_email: Destinatario
        subject: Asunto
        body: Cuerpo
        attachment_data: Adjunto opcional
        html: Si True, body es HTML

    Returns:
        bool: True si se envió exitosamente
    """
    service = EmailService()
    return service.send_email_sync(to_email, subject, body, attachment_data, html)
