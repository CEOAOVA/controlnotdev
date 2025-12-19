"""
ControlNot v2 - Image Preprocessing Service
Preprocesa imagenes para optimizar Claude Vision

IMPORTANTE:
- NO rota imagenes (Claude Vision maneja orientacion automaticamente)
- SI optimiza tamaño para reducir tokens y costos
"""
import io
import base64
from typing import Tuple, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Import Pillow with fallback
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow no instalado. pip install Pillow para preprocesamiento de imagenes")


class ImagePreprocessingService:
    """
    Preprocesa imagenes para Claude Vision

    Operaciones:
    - Redimensionar si excede limites (1568px max)
    - Comprimir si excede 5MB
    - Convertir formatos exoticos a JPEG
    - NO rotar (Claude Vision entiende cualquier orientacion)

    Configuracion desde settings:
    - MAX_IMAGE_DIMENSION: 1568 (recomendado por Anthropic)
    - MAX_IMAGE_SIZE_MB: 5 (limite de Anthropic)
    """

    def __init__(self):
        self.max_dimension = settings.MAX_IMAGE_DIMENSION
        self.max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        self.quality = 85  # JPEG quality inicial

        logger.debug(
            "ImagePreprocessingService inicializado",
            max_dimension=self.max_dimension,
            max_size_mb=settings.MAX_IMAGE_SIZE_MB,
            pillow_available=PILLOW_AVAILABLE
        )

    def preprocess(
        self,
        image_content: bytes,
        filename: str = "image"
    ) -> Tuple[bytes, str]:
        """
        Preprocesa imagen para Claude Vision

        Args:
            image_content: Imagen en bytes
            filename: Nombre del archivo (para determinar formato)

        Returns:
            Tuple[bytes, str]: (imagen procesada, media_type)
        """
        if not PILLOW_AVAILABLE:
            logger.warning("Pillow no disponible, retornando imagen original")
            return image_content, self._detect_media_type_from_bytes(image_content)

        try:
            img = Image.open(io.BytesIO(image_content))
            original_size = len(image_content)

            logger.debug(
                "Preprocesando imagen",
                filename=filename,
                original_size_kb=original_size // 1024,
                dimensions=img.size,
                mode=img.mode
            )

            # Redimensionar si excede maximo
            if max(img.size) > self.max_dimension:
                ratio = self.max_dimension / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                logger.debug("Imagen redimensionada", new_size=new_size)

            # Convertir RGBA/P a RGB (para JPEG)
            if img.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(
                    img,
                    mask=img.split()[-1] if 'A' in img.mode else None
                )
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Guardar como JPEG con compresion
            output = io.BytesIO()
            quality = self.quality

            img.save(output, format='JPEG', quality=quality, optimize=True)
            result = output.getvalue()

            # Si aun excede limite, comprimir mas
            while len(result) > self.max_size_bytes and quality > 30:
                quality -= 10
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                result = output.getvalue()
                logger.debug(
                    "Recomprimiendo",
                    quality=quality,
                    size_kb=len(result) // 1024
                )

            final_size = len(result)

            logger.info(
                "Imagen preprocesada",
                filename=filename,
                original_kb=original_size // 1024,
                final_kb=final_size // 1024,
                reduction_percent=round(
                    (1 - final_size / original_size) * 100, 1
                ) if original_size > 0 else 0
            )

            return result, "image/jpeg"

        except Exception as e:
            logger.error(
                "Error preprocesando imagen",
                filename=filename,
                error=str(e)
            )
            # Retornar original si falla el preprocesamiento
            return image_content, self._detect_media_type_from_bytes(image_content)

    def _detect_media_type_from_bytes(self, content: bytes) -> str:
        """Detecta media type por contenido (magic bytes)"""
        if content.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif content.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
            return 'image/gif'
        elif content.startswith(b'RIFF') and b'WEBP' in content[:12]:
            return 'image/webp'
        return 'image/jpeg'  # Default

    def _detect_media_type(self, filename: str) -> str:
        """Detecta media type por extension"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return {
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
        }.get(ext, 'image/jpeg')

    def to_base64(self, image_content: bytes) -> str:
        """Convierte imagen a base64 para enviar a Claude"""
        return base64.b64encode(image_content).decode('utf-8')

    def preprocess_for_vision(
        self,
        image_content: bytes,
        filename: str = "image"
    ) -> dict:
        """
        Preprocesa imagen y retorna formato listo para Claude Vision

        Args:
            image_content: Imagen en bytes
            filename: Nombre del archivo

        Returns:
            dict: Formato para API de Claude Vision:
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": "<base64>"
                    }
                }
        """
        processed_content, media_type = self.preprocess(image_content, filename)

        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": self.to_base64(processed_content)
            }
        }


# Singleton
_preprocessing_service: Optional[ImagePreprocessingService] = None


def get_image_preprocessing_service() -> ImagePreprocessingService:
    """Factory para obtener instancia singleton del servicio"""
    global _preprocessing_service
    if _preprocessing_service is None:
        _preprocessing_service = ImagePreprocessingService()
    return _preprocessing_service
