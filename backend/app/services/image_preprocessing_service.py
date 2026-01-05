"""
ControlNot v2 - Image Preprocessing Service
Preprocesa imagenes para optimizar Claude Vision y OCR

=== SPECS OFICIALES CLAUDE VISION (Anthropic Docs) ===
https://docs.anthropic.com/en/docs/build-with-claude/vision

| Especificación          | Valor Oficial               |
|-------------------------|------------------------------|
| Formatos soportados     | JPEG, PNG, GIF, WebP        |
| Tamaño máximo           | 8000x8000 px (rechazado)    |
| Tamaño óptimo           | ≤1568px en ambas dims       |
| Megapíxeles óptimos     | ≤1.15 MP                    |
| Tamaño mínimo efectivo  | >200px (menor degrada)      |
| Fórmula de tokens       | tokens = (width*height)/750 |
| Límite por request      | 100 imágenes API            |
| Peso máximo             | 5MB por imagen (API)        |

Best Practices:
- "Resize images to no more than 1.15 megapixels"
- "Claude may hallucinate on low-quality, rotated, or very small images"
- CLAHE para mejora de contraste adaptativo (PyImageSearch)
- Denoising para reducir ruido de compresión WhatsApp
- Deskewing para documentos inclinados

IMPORTANTE:
- NO rota imagenes (Claude Vision maneja orientacion automaticamente)
- SI optimiza tamaño para reducir tokens y costos
- SI mejora calidad para documentos dificiles
"""
import io
import base64
from typing import Tuple, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Import OpenCV with fallback
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning(
        "OpenCV no instalado. pip install opencv-python-headless "
        "para preprocesamiento avanzado de imagenes"
    )

# Import Pillow with fallback
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow no instalado. pip install Pillow para preprocesamiento de imagenes")


class ImagePreprocessingService:
    """
    Preprocesa imagenes para Claude Vision según specs oficiales de Anthropic.

    === SPECS OFICIALES (docs.anthropic.com) ===
    - MAX_DIMENSION: 1568px (óptimo, >8000px rechazado)
    - MIN_DIMENSION: 200px (menor degrada calidad)
    - MAX_MEGAPIXELS: 1.15 MP (reduce tokens)
    - MAX_SIZE: 5MB por imagen
    - TOKENS: (width * height) / 750

    Operaciones:
    - Redimensionar a ≤1568px Y ≤1.15MP
    - Validar ≥200px mínimo
    - Comprimir si excede 5MB
    - Convertir formatos exóticos a JPEG
    - NO rotar (Claude maneja orientación)
    """

    # Constantes oficiales de Anthropic
    CLAUDE_MAX_DIMENSION = 1568   # Oficial: óptimo
    CLAUDE_MIN_DIMENSION = 200    # Oficial: mínimo efectivo
    CLAUDE_MAX_MEGAPIXELS = 1.15  # Oficial: "no more than 1.15 megapixels"
    CLAUDE_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
    CLAUDE_TOKENS_DIVISOR = 750   # tokens = (w*h) / 750

    def __init__(self):
        self.max_dimension = getattr(settings, 'MAX_IMAGE_DIMENSION', self.CLAUDE_MAX_DIMENSION)
        self.min_dimension = getattr(settings, 'MIN_IMAGE_DIMENSION', self.CLAUDE_MIN_DIMENSION)
        self.max_megapixels = getattr(settings, 'MAX_MEGAPIXELS', self.CLAUDE_MAX_MEGAPIXELS)
        self.max_size_bytes = getattr(settings, 'MAX_IMAGE_SIZE_MB', 5) * 1024 * 1024
        self.quality = 85  # JPEG quality inicial

        logger.debug(
            "ImagePreprocessingService inicializado (Claude Vision specs)",
            max_dimension=self.max_dimension,
            min_dimension=self.min_dimension,
            max_megapixels=self.max_megapixels,
            max_size_mb=self.max_size_bytes // (1024 * 1024),
            pillow_available=PILLOW_AVAILABLE
        )

    def calculate_tokens(self, width: int, height: int) -> int:
        """
        Calcula tokens de Claude Vision según fórmula oficial.

        Fórmula oficial: tokens = (width * height) / 750
        Fuente: docs.anthropic.com/en/docs/build-with-claude/vision
        """
        return int((width * height) / self.CLAUDE_TOKENS_DIVISOR)

    def calculate_megapixels(self, width: int, height: int) -> float:
        """Calcula megapíxeles de una imagen."""
        return (width * height) / 1_000_000

    def preprocess(
        self,
        image_content: bytes,
        filename: str = "image"
    ) -> Tuple[bytes, str]:
        """
        Preprocesa imagen para Claude Vision según specs oficiales.

        Validaciones (docs.anthropic.com):
        - Si >1568px o >1.15MP: resize
        - Si <200px: warning (degrada calidad)
        - Si >5MB: comprimir

        Args:
            image_content: Imagen en bytes
            filename: Nombre del archivo

        Returns:
            Tuple[bytes, str]: (imagen procesada, media_type)
        """
        if not PILLOW_AVAILABLE:
            logger.warning("Pillow no disponible, retornando imagen original")
            return image_content, self._detect_media_type_from_bytes(image_content)

        try:
            img = Image.open(io.BytesIO(image_content))
            original_size = len(image_content)
            original_mp = self.calculate_megapixels(img.width, img.height)
            original_tokens = self.calculate_tokens(img.width, img.height)

            logger.debug(
                "Preprocesando imagen (Claude Vision specs)",
                filename=filename,
                original_size_kb=original_size // 1024,
                dimensions=img.size,
                megapixels=round(original_mp, 2),
                estimated_tokens=original_tokens,
                mode=img.mode
            )

            # Warning si imagen muy pequeña (<200px)
            if min(img.size) < self.min_dimension:
                logger.warning(
                    "Imagen muy pequeña (Anthropic: >200px recomendado)",
                    filename=filename,
                    min_dimension=min(img.size),
                    recommended_min=self.min_dimension
                )

            # Redimensionar si excede máximo de dimensión
            needs_resize = max(img.size) > self.max_dimension

            # También redimensionar si excede megapíxeles (1.15MP)
            current_mp = self.calculate_megapixels(img.width, img.height)
            if current_mp > self.max_megapixels:
                needs_resize = True
                logger.debug(
                    "Imagen excede megapíxeles óptimos",
                    current_mp=round(current_mp, 2),
                    max_mp=self.max_megapixels
                )

            if needs_resize:
                # Calcular ratio por dimensión máxima
                dim_ratio = self.max_dimension / max(img.size) if max(img.size) > self.max_dimension else 1.0

                # Calcular ratio por megapíxeles
                mp_ratio = (self.max_megapixels / current_mp) ** 0.5 if current_mp > self.max_megapixels else 1.0

                # Usar el ratio más restrictivo
                ratio = min(dim_ratio, mp_ratio)
                new_size = (int(img.width * ratio), int(img.height * ratio))

                # Asegurar que no sea menor que el mínimo
                if min(new_size) < self.min_dimension:
                    scale_up = self.min_dimension / min(new_size)
                    new_size = (int(new_size[0] * scale_up), int(new_size[1] * scale_up))

                img = img.resize(new_size, Image.LANCZOS)
                new_mp = self.calculate_megapixels(img.width, img.height)
                new_tokens = self.calculate_tokens(img.width, img.height)
                logger.debug(
                    "Imagen redimensionada (Claude Vision optimizado)",
                    new_size=new_size,
                    new_mp=round(new_mp, 2),
                    new_tokens=new_tokens,
                    token_reduction=f"{100 - (new_tokens/original_tokens*100):.1f}%"
                )

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

    # =========================================
    # NUEVAS FUNCIONES DE PREPROCESAMIENTO 2025
    # =========================================

    def apply_clahe(
        self,
        image_content: bytes,
        clip_limit: float = 2.0,
        tile_grid_size: Tuple[int, int] = (8, 8)
    ) -> bytes:
        """
        Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization).

        Mejora el contraste local sin amplificar ruido excesivamente.
        Ideal para: documentos desvanecidos, fotocopias, escaneos de baja calidad.

        Args:
            image_content: Imagen en bytes
            clip_limit: Limite de contraste (2.0-5.0, mayor = mas contraste y ruido)
            tile_grid_size: Tamaño de tiles para ecualizacion local

        Returns:
            Imagen mejorada en bytes (JPEG)
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV no disponible para CLAHE")
            return image_content

        try:
            # Convertir bytes a imagen OpenCV
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_content

            # Convertir a LAB para aplicar CLAHE solo al canal L (luminosidad)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)

            # Aplicar CLAHE al canal L
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            l_channel_clahe = clahe.apply(l_channel)

            # Reconstruir imagen
            lab_clahe = cv2.merge([l_channel_clahe, a_channel, b_channel])
            result = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

            # Codificar a JPEG
            _, encoded = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])

            logger.debug("CLAHE aplicado", clip_limit=clip_limit)
            return encoded.tobytes()

        except Exception as e:
            logger.error("Error aplicando CLAHE", error=str(e))
            return image_content

    def denoise_image(
        self,
        image_content: bytes,
        strength: int = 10
    ) -> bytes:
        """
        Reduce ruido en la imagen preservando bordes.

        Usa Non-local Means Denoising, efectivo para ruido de compresion
        (WhatsApp, escaneos).

        Args:
            image_content: Imagen en bytes
            strength: Fuerza del filtro (5-15, mayor = mas suavizado)

        Returns:
            Imagen sin ruido en bytes (JPEG)
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV no disponible para denoising")
            return image_content

        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_content

            # fastNlMeansDenoisingColored para imagenes a color
            denoised = cv2.fastNlMeansDenoisingColored(
                img,
                None,
                h=strength,           # Filtro para luminancia
                hForColorComponents=strength,  # Filtro para color
                templateWindowSize=7,
                searchWindowSize=21
            )

            _, encoded = cv2.imencode('.jpg', denoised, [cv2.IMWRITE_JPEG_QUALITY, 90])

            logger.debug("Denoising aplicado", strength=strength)
            return encoded.tobytes()

        except Exception as e:
            logger.error("Error en denoising", error=str(e))
            return image_content

    def adaptive_binarize(
        self,
        image_content: bytes,
        block_size: int = 11,
        constant: int = 2
    ) -> bytes:
        """
        Aplica binarizacion adaptativa.

        Convierte a blanco y negro usando umbral local, efectivo para
        documentos con sellos, manchas o fondos irregulares.

        NOTA: Esta funcion retorna imagen en escala de grises.
        Usar solo cuando el OCR lo requiera especificamente.

        Args:
            image_content: Imagen en bytes
            block_size: Tamaño de region para umbral local (debe ser impar)
            constant: Constante a restar del umbral calculado

        Returns:
            Imagen binarizada en bytes (JPEG grayscale)
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV no disponible para binarizacion")
            return image_content

        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

            if img is None:
                return image_content

            # Binarizacion adaptativa con umbral gaussiano
            binary = cv2.adaptiveThreshold(
                img,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                block_size,
                constant
            )

            _, encoded = cv2.imencode('.jpg', binary, [cv2.IMWRITE_JPEG_QUALITY, 95])

            logger.debug("Binarizacion adaptativa aplicada", block_size=block_size)
            return encoded.tobytes()

        except Exception as e:
            logger.error("Error en binarizacion", error=str(e))
            return image_content

    def deskew_image(self, image_content: bytes) -> bytes:
        """
        Corrige inclinacion del documento.

        Detecta el angulo de inclinacion y rota para enderezar.
        Tesseract y otros OCR pierden precision con >2 grados de skew.

        Args:
            image_content: Imagen en bytes

        Returns:
            Imagen enderezada en bytes (JPEG)
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV no disponible para deskewing")
            return image_content

        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_content

            # Convertir a grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Invertir colores (texto blanco sobre fondo negro)
            gray = cv2.bitwise_not(gray)

            # Umbral para obtener solo el texto
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # Encontrar coordenadas de pixeles no-cero
            coords = np.column_stack(np.where(thresh > 0))

            if len(coords) < 100:  # No hay suficiente contenido
                return image_content

            # Calcular angulo con minAreaRect
            angle = cv2.minAreaRect(coords)[-1]

            # Ajustar angulo
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Solo corregir si la inclinacion es significativa
            if abs(angle) < 0.5:
                logger.debug("Skew insignificante, no se corrige", angle=angle)
                return image_content

            if abs(angle) > 15:
                logger.warning("Skew muy grande, podria ser orientacion incorrecta", angle=angle)
                return image_content

            # Rotar imagen
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img,
                rotation_matrix,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )

            _, encoded = cv2.imencode('.jpg', rotated, [cv2.IMWRITE_JPEG_QUALITY, 90])

            logger.debug("Deskewing aplicado", angle=round(angle, 2))
            return encoded.tobytes()

        except Exception as e:
            logger.error("Error en deskewing", error=str(e))
            return image_content

    def sharpen_image(
        self,
        image_content: bytes,
        strength: float = 1.0
    ) -> bytes:
        """
        Mejora la nitidez de la imagen.

        Usa filtro unsharp mask para realzar bordes.

        Args:
            image_content: Imagen en bytes
            strength: Fuerza del sharpening (0.5-2.0)

        Returns:
            Imagen con nitidez mejorada en bytes (JPEG)
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV no disponible para sharpening")
            return image_content

        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_content

            # Crear version borrosa
            gaussian = cv2.GaussianBlur(img, (0, 0), 3)

            # Unsharp mask: original + (original - borroso) * strength
            sharpened = cv2.addWeighted(img, 1.0 + strength, gaussian, -strength, 0)

            _, encoded = cv2.imencode('.jpg', sharpened, [cv2.IMWRITE_JPEG_QUALITY, 90])

            logger.debug("Sharpening aplicado", strength=strength)
            return encoded.tobytes()

        except Exception as e:
            logger.error("Error en sharpening", error=str(e))
            return image_content

    def preprocess_for_quality(
        self,
        image_content: bytes,
        quality_level: str,
        filename: str = "image"
    ) -> Tuple[bytes, str]:
        """
        Pipeline de preprocesamiento adaptativo segun nivel de calidad.

        Args:
            image_content: Imagen en bytes
            quality_level: "high", "medium", "low", o "reject"
            filename: Nombre del archivo

        Returns:
            Tuple[bytes, str]: (imagen procesada, media_type)
        """
        logger.info(
            "Preprocesamiento adaptativo",
            quality_level=quality_level,
            filename=filename
        )

        if quality_level == "high":
            # Solo resize estandar para Claude
            return self.preprocess(image_content, filename)

        elif quality_level == "medium":
            # Mejoras ligeras
            processed = self.apply_clahe(image_content, clip_limit=2.0)
            processed = self.denoise_image(processed, strength=7)
            return self.preprocess(processed, filename)

        elif quality_level == "low":
            # Preprocesamiento agresivo
            processed = self.apply_clahe(image_content, clip_limit=3.0)
            processed = self.denoise_image(processed, strength=10)
            processed = self.sharpen_image(processed, strength=0.8)
            processed = self.deskew_image(processed)
            return self.preprocess(processed, filename)

        else:  # reject o desconocido
            # Intentar todo lo posible
            logger.warning("Calidad REJECT, aplicando todas las mejoras")
            processed = self.apply_clahe(image_content, clip_limit=4.0)
            processed = self.denoise_image(processed, strength=12)
            processed = self.sharpen_image(processed, strength=1.0)
            processed = self.deskew_image(processed)
            return self.preprocess(processed, filename)

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
