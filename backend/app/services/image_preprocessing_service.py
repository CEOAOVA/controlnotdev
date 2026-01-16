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

    # =========================================
    # FUNCIONES DE PREPROCESAMIENTO WHATSAPP
    # Mejoras para imágenes de documentos enviados por WhatsApp
    # =========================================

    def _check_exif_orientation(self, img: Image.Image) -> int:
        """
        Verifica el tag EXIF Orientation para determinar rotación.

        EXIF Orientation values:
        1 = Normal (0°)
        3 = Rotado 180°
        6 = Rotado 90° CW (necesita rotar 270° CCW para corregir)
        8 = Rotado 270° CW (necesita rotar 90° CCW para corregir)

        Returns:
            int: Ángulo de corrección necesario (0, 90, 180, 270)
        """
        try:
            from PIL.ExifTags import TAGS
            exif = img._getexif()
            if exif:
                for tag, value in exif.items():
                    if TAGS.get(tag) == 'Orientation':
                        orientation_map = {
                            1: 0,    # Normal
                            3: 180,  # Rotado 180
                            6: 270,  # Rotado 90 CW -> corregir con 270 CCW
                            8: 90,   # Rotado 270 CW -> corregir con 90 CCW
                        }
                        return orientation_map.get(value, 0)
        except Exception:
            pass
        return 0

    def _detect_orientation_by_text_lines(self, gray: np.ndarray) -> int:
        """
        Detecta orientación analizando la dirección de líneas de texto.

        Las líneas de texto en un documento correctamente orientado son horizontales.
        Si predominan líneas verticales, el documento está rotado 90°.

        Returns:
            int: Ángulo de corrección sugerido (0, 90, 180, 270)
        """
        if not CV2_AVAILABLE:
            return 0

        try:
            # Detectar bordes
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # Detectar líneas con Hough
            lines = cv2.HoughLinesP(
                edges, 1, np.pi/180,
                threshold=80,
                minLineLength=50,
                maxLineGap=10
            )

            if lines is None or len(lines) < 5:
                return 0

            horizontal_count = 0
            vertical_count = 0

            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Calcular ángulo de la línea
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

                # Líneas horizontales: ángulo cerca de 0° o 180°
                if -20 < angle < 20 or 160 < abs(angle) <= 180:
                    horizontal_count += 1
                # Líneas verticales: ángulo cerca de 90° o -90°
                elif 70 < abs(angle) < 110:
                    vertical_count += 1

            logger.debug(
                "Análisis de líneas de texto",
                horizontal=horizontal_count,
                vertical=vertical_count
            )

            # Si hay significativamente más líneas verticales, está rotado 90°
            if vertical_count > horizontal_count * 1.5 and vertical_count > 10:
                return 90

            return 0

        except Exception as e:
            logger.warning(f"Error en detección de líneas: {e}")
            return 0

    def _rotate_image_cv2(self, img: np.ndarray, angle: int) -> np.ndarray:
        """
        Rota imagen en múltiplos de 90 grados sin pérdida de calidad.

        Args:
            img: Imagen OpenCV (numpy array)
            angle: Ángulo (0, 90, 180, 270)

        Returns:
            Imagen rotada
        """
        if angle == 0:
            return img
        elif angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    def detect_and_correct_orientation(
        self,
        image_content: bytes
    ) -> Tuple[bytes, int]:
        """
        Detecta y corrige rotaciones de 90°, 180°, 270° en documentos.

        Estrategia multi-método:
        1. EXIF orientation tag (WhatsApp a veces lo preserva)
        2. Análisis de líneas de texto (detecta orientación del contenido)
        3. Heurística de aspect ratio (documentos típicamente son verticales)

        Args:
            image_content: Imagen en bytes

        Returns:
            Tuple[bytes, int]: (imagen corregida, ángulo de rotación aplicado)
        """
        if not CV2_AVAILABLE or not PILLOW_AVAILABLE:
            logger.warning("OpenCV/Pillow no disponible para corrección de orientación")
            return image_content, 0

        try:
            # 1. Verificar EXIF
            pil_img = Image.open(io.BytesIO(image_content))
            exif_rotation = self._check_exif_orientation(pil_img)

            if exif_rotation != 0:
                logger.info(f"EXIF indica rotación de {exif_rotation}°")
                # Rotar usando PIL para mantener calidad
                rotation_map = {
                    90: Image.Transpose.ROTATE_90,
                    180: Image.Transpose.ROTATE_180,
                    270: Image.Transpose.ROTATE_270
                }
                if exif_rotation in rotation_map:
                    pil_img = pil_img.transpose(rotation_map[exif_rotation])
                    output = io.BytesIO()
                    pil_img.save(output, format='JPEG', quality=95)
                    return output.getvalue(), exif_rotation

            # 2. Convertir a OpenCV para análisis
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_content, 0

            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 3. Análisis de líneas de texto
            text_rotation = self._detect_orientation_by_text_lines(gray)

            if text_rotation != 0:
                logger.info(f"Análisis de texto sugiere rotación de {text_rotation}°")
                rotated = self._rotate_image_cv2(img, text_rotation)
                _, encoded = cv2.imencode('.jpg', rotated, [cv2.IMWRITE_JPEG_QUALITY, 95])
                return encoded.tobytes(), text_rotation

            # 4. Heurística de aspect ratio (fallback)
            # Documentos como INE, actas son más altos que anchos
            aspect = max(h, w) / min(h, w)

            if aspect > 1.2 and w > h:
                # Imagen horizontal pero documentos son verticales
                # Podría estar rotada 90° - verificar con más análisis
                logger.debug(
                    "Aspect ratio sugiere posible rotación",
                    width=w, height=h, aspect=round(aspect, 2)
                )
                # No rotar automáticamente solo por aspect ratio
                # ya que podría ser un documento legítimamente horizontal

            return image_content, 0

        except Exception as e:
            logger.error(f"Error en corrección de orientación: {e}")
            return image_content, 0

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        Ordena 4 puntos en sentido: top-left, top-right, bottom-right, bottom-left.
        Necesario para transformación de perspectiva.
        """
        rect = np.zeros((4, 2), dtype="float32")

        # Top-left tiene la menor suma (x+y), bottom-right la mayor
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # Top-right tiene la menor diferencia (y-x), bottom-left la mayor
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def _four_point_transform(self, img: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Aplica transformación de perspectiva para enderezar documento inclinado.

        Args:
            img: Imagen OpenCV
            pts: 4 puntos del contorno del documento

        Returns:
            Documento enderezado y recortado
        """
        rect = self._order_points(pts)
        (tl, tr, br, bl) = rect

        # Calcular dimensiones del documento enderezado
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Asegurar dimensiones mínimas
        maxWidth = max(maxWidth, 100)
        maxHeight = max(maxHeight, 100)

        # Puntos destino (rectángulo perfecto)
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # Calcular matriz de transformación y aplicar
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

        return warped

    def detect_and_crop_document(
        self,
        image_content: bytes,
        min_area_ratio: float = 0.15,
        max_area_ratio: float = 0.95
    ) -> Tuple[bytes, dict]:
        """
        Detecta el documento en la imagen y lo recorta, eliminando fondos.

        Elimina elementos contaminantes como:
        - Carpetas de notaría
        - Escritorios/mesas
        - Otros documentos en el fondo

        Args:
            image_content: Imagen original
            min_area_ratio: Área mínima del documento (15% de imagen)
            max_area_ratio: Área máxima (95%, evita seleccionar toda la imagen)

        Returns:
            Tuple[bytes, dict]: (imagen recortada, metadatos del recorte)
        """
        if not CV2_AVAILABLE:
            return image_content, {"cropped": False, "reason": "OpenCV not available"}

        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_content, {"cropped": False, "reason": "Invalid image"}

            original_height, original_width = img.shape[:2]
            total_area = original_height * original_width

            # 1. Preprocesamiento para detección de contornos
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 2. Detección de bordes con Canny
            edges = cv2.Canny(blurred, 30, 200)

            # 3. Dilatar para conectar bordes cercanos
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(edges, kernel, iterations=2)

            # 4. Encontrar contornos
            contours, _ = cv2.findContours(
                dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                return image_content, {"cropped": False, "reason": "No contours found"}

            # 5. Filtrar contornos por área y rectangularidad
            valid_contours = []

            for contour in contours:
                area = cv2.contourArea(contour)
                area_ratio = area / total_area

                if area_ratio < min_area_ratio or area_ratio > max_area_ratio:
                    continue

                # Aproximar a polígono
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

                # Buscar rectángulos (4-6 vértices)
                if 4 <= len(approx) <= 6:
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box_area = cv2.contourArea(box)

                    rectangularity = area / box_area if box_area > 0 else 0

                    if rectangularity > 0.65:
                        valid_contours.append({
                            "contour": contour,
                            "approx": approx,
                            "area": area,
                            "area_ratio": area_ratio,
                            "rectangularity": rectangularity
                        })

            if not valid_contours:
                return image_content, {"cropped": False, "reason": "No rectangular contours"}

            # 6. Seleccionar el mejor contorno (mayor área × rectangularidad)
            best = max(valid_contours, key=lambda x: x["area"] * x["rectangularity"])

            # 7. Aplicar transformación de perspectiva o recorte simple
            if len(best["approx"]) == 4:
                # Transformación de perspectiva para documentos inclinados
                cropped = self._four_point_transform(
                    img, best["approx"].reshape(4, 2)
                )
            else:
                # Recorte con bounding box
                x, y, w, h = cv2.boundingRect(best["contour"])
                # Agregar padding del 1%
                pad = int(min(w, h) * 0.01)
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(original_width, x + w + pad)
                y2 = min(original_height, y + h + pad)
                cropped = img[y1:y2, x1:x2]

            # 8. Codificar resultado
            _, encoded = cv2.imencode('.jpg', cropped, [cv2.IMWRITE_JPEG_QUALITY, 95])

            logger.info(
                "Documento recortado exitosamente",
                original_size=(original_width, original_height),
                cropped_size=cropped.shape[:2][::-1],
                area_ratio=round(best["area_ratio"], 2)
            )

            return encoded.tobytes(), {
                "cropped": True,
                "original_size": (original_width, original_height),
                "cropped_size": cropped.shape[:2][::-1],
                "area_ratio": round(best["area_ratio"], 3),
                "rectangularity": round(best["rectangularity"], 3)
            }

        except Exception as e:
            logger.error(f"Error detectando documento: {e}")
            return image_content, {"cropped": False, "reason": str(e)}

    def segment_multiple_documents(
        self,
        image_content: bytes,
        min_doc_area_ratio: float = 0.08,
        max_documents: int = 4
    ) -> list:
        """
        Detecta y segmenta múltiples documentos en una sola imagen.

        Casos de uso:
        - 2 INEs (anverso/reverso) en una foto
        - Múltiples documentos fotografiados juntos

        Args:
            image_content: Imagen con posibles múltiples documentos
            min_doc_area_ratio: Área mínima de cada documento (8%)
            max_documents: Máximo de documentos a extraer

        Returns:
            List[Tuple[bytes, dict]]: Lista de (imagen_recortada, metadatos)
        """
        if not CV2_AVAILABLE:
            return [(image_content, {"segmented": False, "reason": "OpenCV not available"})]

        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return [(image_content, {"segmented": False, "reason": "Invalid image"})]

            original_height, original_width = img.shape[:2]
            total_area = original_height * original_width

            # Preprocesamiento
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Threshold adaptativo para manejar iluminación irregular
            thresh = cv2.adaptiveThreshold(
                blurred, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )

            # Operaciones morfológicas para limpiar
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

            # También probar con Canny para mejor detección de bordes
            edges = cv2.Canny(blurred, 30, 200)
            edges_dilated = cv2.dilate(edges, kernel, iterations=2)

            # Combinar ambos métodos
            combined = cv2.bitwise_or(closed, edges_dilated)

            # Encontrar contornos
            contours, _ = cv2.findContours(
                combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Filtrar contornos válidos
            documents = []

            for contour in contours:
                area = cv2.contourArea(contour)
                area_ratio = area / total_area

                if area_ratio < min_doc_area_ratio:
                    continue

                # Verificar rectangularidad
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

                if 4 <= len(approx) <= 6:
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box_area = cv2.contourArea(box)
                    rectangularity = area / box_area if box_area > 0 else 0

                    if rectangularity > 0.6:
                        x, y, w, h = cv2.boundingRect(contour)
                        documents.append({
                            "contour": contour,
                            "approx": approx,
                            "area": area,
                            "area_ratio": area_ratio,
                            "rectangularity": rectangularity,
                            "bounding_rect": (x, y, w, h)
                        })

            # Si hay 0 o 1 documento, usar función de recorte simple
            if len(documents) <= 1:
                cropped, meta = self.detect_and_crop_document(image_content)
                return [(cropped, {**meta, "segmented": False, "total_documents": 1})]

            # Ordenar por posición (arriba a abajo, izquierda a derecha)
            documents.sort(key=lambda d: (d["bounding_rect"][1], d["bounding_rect"][0]))

            # Limitar al máximo
            documents = documents[:max_documents]

            # Recortar cada documento
            results = []
            for i, doc in enumerate(documents):
                x, y, w, h = doc["bounding_rect"]

                # Padding del 2%
                pad_x = int(w * 0.02)
                pad_y = int(h * 0.02)

                x1 = max(0, x - pad_x)
                y1 = max(0, y - pad_y)
                x2 = min(original_width, x + w + pad_x)
                y2 = min(original_height, y + h + pad_y)

                cropped = img[y1:y2, x1:x2]

                _, encoded = cv2.imencode('.jpg', cropped, [cv2.IMWRITE_JPEG_QUALITY, 95])

                results.append((encoded.tobytes(), {
                    "segmented": True,
                    "document_index": i + 1,
                    "total_documents": len(documents),
                    "position": (x, y),
                    "size": (w, h),
                    "area_ratio": round(doc["area_ratio"], 3)
                }))

            logger.info(
                "Múltiples documentos segmentados",
                total_found=len(results)
            )

            return results

        except Exception as e:
            logger.error(f"Error segmentando documentos: {e}")
            return [(image_content, {"segmented": False, "error": str(e)})]

    def preprocess_whatsapp_image(
        self,
        image_content: bytes,
        filename: str = "image",
        auto_rotate: bool = True,
        auto_crop: bool = True,
        auto_segment: bool = False
    ) -> Tuple[bytes, str, dict]:
        """
        Pipeline completo de preprocesamiento para imágenes de WhatsApp.

        Orden de operaciones:
        1. Corregir orientación (90°/180°/270°)
        2. Detectar y recortar documento
        3. CLAHE para contraste
        4. Denoising para artefactos de compresión JPEG
        5. Sharpening para recuperar detalles
        6. Deskew para inclinaciones pequeñas
        7. Resize para Claude Vision

        Args:
            image_content: Imagen original de WhatsApp
            filename: Nombre del archivo
            auto_rotate: Corregir rotación automáticamente
            auto_crop: Recortar documento automáticamente
            auto_segment: Segmentar múltiples documentos

        Returns:
            Tuple[bytes, str, dict]: (imagen procesada, media_type, metadatos)
        """
        metadata = {
            "original_size": len(image_content),
            "steps_applied": [],
            "whatsapp_pipeline": True
        }

        processed = image_content

        # 1. Corrección de orientación
        if auto_rotate:
            processed, rotation = self.detect_and_correct_orientation(processed)
            if rotation != 0:
                metadata["steps_applied"].append(f"rotation_{rotation}")
                metadata["rotation_applied"] = rotation

        # 2. Detección y recorte de documento
        if auto_crop:
            processed, crop_info = self.detect_and_crop_document(processed)
            if crop_info.get("cropped"):
                metadata["steps_applied"].append("document_crop")
                metadata["crop_info"] = crop_info

        # 3. CLAHE para mejorar contraste (importante para WhatsApp)
        processed = self.apply_clahe(processed, clip_limit=2.5, tile_grid_size=(8, 8))
        metadata["steps_applied"].append("clahe")

        # 4. Denoising para artefactos de compresión JPEG
        processed = self.denoise_image(processed, strength=8)
        metadata["steps_applied"].append("denoise")

        # 5. Sharpening para recuperar detalles
        processed = self.sharpen_image(processed, strength=0.5)
        metadata["steps_applied"].append("sharpen")

        # 6. Deskew para inclinaciones pequeñas
        processed = self.deskew_image(processed)
        metadata["steps_applied"].append("deskew")

        # 7. Resize final para Claude Vision
        processed, media_type = self.preprocess(processed, filename)
        metadata["steps_applied"].append("resize")

        metadata["final_size"] = len(processed)
        metadata["size_reduction_percent"] = round(
            (1 - len(processed) / metadata["original_size"]) * 100, 1
        ) if metadata["original_size"] > 0 else 0

        logger.info(
            "WhatsApp image preprocessed",
            filename=filename,
            steps=len(metadata["steps_applied"]),
            size_reduction=f"{metadata['size_reduction_percent']}%"
        )

        return processed, media_type, metadata


# Singleton
_preprocessing_service: Optional[ImagePreprocessingService] = None


def get_image_preprocessing_service() -> ImagePreprocessingService:
    """Factory para obtener instancia singleton del servicio"""
    global _preprocessing_service
    if _preprocessing_service is None:
        _preprocessing_service = ImagePreprocessingService()
    return _preprocessing_service
