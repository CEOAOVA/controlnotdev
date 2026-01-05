"""
ControlNot v2 - Document Quality Assessment Service
Evalua la calidad de imagenes de documentos para optimizar el pipeline OCR.

Best Practices 2025:
- Laplacian variance para deteccion de blur (PyImageSearch)
- Analisis de histograma para contraste
- Umbrales adaptativos segun tipo de documento
"""
import io
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
import structlog

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
        "para evaluacion de calidad de documentos"
    )

# Import Pillow as fallback
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class QualityLevel(str, Enum):
    """Niveles de calidad de imagen"""
    HIGH = "high"        # Procesar normal
    MEDIUM = "medium"    # Preprocesamiento ligero
    LOW = "low"          # Preprocesamiento agresivo + retry
    REJECT = "reject"    # Solicitar mejor imagen


@dataclass
class QualityReport:
    """Reporte detallado de calidad de imagen"""
    # Scores individuales (0-100, mayor es mejor)
    blur_score: float = 0.0
    contrast_score: float = 0.0
    brightness_score: float = 0.0
    resolution_score: float = 0.0

    # Nivel general calculado
    overall_level: QualityLevel = QualityLevel.MEDIUM

    # Recomendaciones de mejora
    recommendations: List[str] = field(default_factory=list)

    # Metricas raw para debugging
    raw_metrics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "blur_score": round(self.blur_score, 2),
            "contrast_score": round(self.contrast_score, 2),
            "brightness_score": round(self.brightness_score, 2),
            "resolution_score": round(self.resolution_score, 2),
            "overall_level": self.overall_level.value,
            "recommendations": self.recommendations,
            "raw_metrics": self.raw_metrics
        }


class DocumentQualityService:
    """
    Servicio de evaluacion de calidad de documentos.

    Umbrales basados en best practices de PyImageSearch y Google Vision:
    - BLUR_THRESHOLD: 100 (Laplacian variance)
    - CONTRAST_MIN: 40 (std deviation of histogram)
    - BRIGHTNESS_RANGE: 80-200 (mean pixel value)
    - MIN_RESOLUTION: 200px (Claude Vision minimum)
    """

    # Umbrales de calidad (ajustables segun dataset)
    BLUR_THRESHOLD_HIGH = 150    # Muy nitido
    BLUR_THRESHOLD_MEDIUM = 80   # Aceptable
    BLUR_THRESHOLD_LOW = 40      # Borroso

    CONTRAST_THRESHOLD_HIGH = 60
    CONTRAST_THRESHOLD_MEDIUM = 35
    CONTRAST_THRESHOLD_LOW = 20

    BRIGHTNESS_OPTIMAL_MIN = 80
    BRIGHTNESS_OPTIMAL_MAX = 200

    MIN_RESOLUTION = 200         # Pixeles en lado menor
    GOOD_RESOLUTION = 500        # Resolucion buena

    def __init__(self):
        logger.debug(
            "DocumentQualityService inicializado",
            cv2_available=CV2_AVAILABLE,
            pillow_available=PILLOW_AVAILABLE
        )

    def assess_quality(self, image_content: bytes) -> QualityReport:
        """
        Evalua la calidad de una imagen de documento.

        Args:
            image_content: Imagen en bytes

        Returns:
            QualityReport con scores y recomendaciones
        """
        report = QualityReport()

        if not CV2_AVAILABLE:
            logger.warning("OpenCV no disponible, retornando calidad MEDIUM por defecto")
            report.overall_level = QualityLevel.MEDIUM
            report.recommendations.append("Instalar opencv-python-headless para evaluacion de calidad")
            return report

        try:
            # Convertir bytes a imagen OpenCV
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("No se pudo decodificar imagen")
                report.overall_level = QualityLevel.REJECT
                report.recommendations.append("Imagen corrupta o formato no soportado")
                return report

            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 1. BLUR DETECTION (Laplacian variance)
            blur_score, laplacian_var = self._assess_blur(gray)
            report.blur_score = blur_score
            report.raw_metrics["laplacian_variance"] = laplacian_var

            # 2. CONTRAST ANALYSIS
            contrast_score, histogram_std = self._assess_contrast(gray)
            report.contrast_score = contrast_score
            report.raw_metrics["histogram_std"] = histogram_std

            # 3. BRIGHTNESS CHECK
            brightness_score, mean_brightness = self._assess_brightness(gray)
            report.brightness_score = brightness_score
            report.raw_metrics["mean_brightness"] = mean_brightness

            # 4. RESOLUTION CHECK
            resolution_score, dimensions = self._assess_resolution(img)
            report.resolution_score = resolution_score
            report.raw_metrics["dimensions"] = dimensions

            # Calcular nivel general
            report.overall_level = self._calculate_overall_level(report)

            # Generar recomendaciones
            report.recommendations = self._generate_recommendations(report)

            logger.info(
                "Calidad de imagen evaluada",
                blur_score=report.blur_score,
                contrast_score=report.contrast_score,
                brightness_score=report.brightness_score,
                resolution_score=report.resolution_score,
                overall_level=report.overall_level.value
            )

            return report

        except Exception as e:
            logger.error("Error evaluando calidad", error=str(e))
            report.overall_level = QualityLevel.MEDIUM
            report.recommendations.append(f"Error en evaluacion: {str(e)}")
            return report

    def _assess_blur(self, gray: 'np.ndarray') -> tuple:
        """
        Evalua nitidez usando Laplacian variance.

        El operador Laplaciano detecta bordes. Alta varianza = imagen nitida.
        Threshold ~100 recomendado por PyImageSearch.
        """
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        # Convertir a score 0-100
        if variance >= self.BLUR_THRESHOLD_HIGH:
            score = 100
        elif variance >= self.BLUR_THRESHOLD_MEDIUM:
            # Interpolar entre MEDIUM y HIGH
            score = 50 + 50 * (variance - self.BLUR_THRESHOLD_MEDIUM) / (self.BLUR_THRESHOLD_HIGH - self.BLUR_THRESHOLD_MEDIUM)
        elif variance >= self.BLUR_THRESHOLD_LOW:
            # Interpolar entre LOW y MEDIUM
            score = 25 + 25 * (variance - self.BLUR_THRESHOLD_LOW) / (self.BLUR_THRESHOLD_MEDIUM - self.BLUR_THRESHOLD_LOW)
        else:
            # Muy borroso
            score = max(0, 25 * variance / self.BLUR_THRESHOLD_LOW)

        return min(100, score), round(variance, 2)

    def _assess_contrast(self, gray: 'np.ndarray') -> tuple:
        """
        Evalua contraste usando desviacion estandar del histograma.

        Alto std = buen contraste entre texto y fondo.
        """
        histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
        std_dev = np.std(histogram)

        # Tambien calcular std de los pixeles directamente
        pixel_std = np.std(gray)

        # Usar pixel_std como metrica principal
        if pixel_std >= self.CONTRAST_THRESHOLD_HIGH:
            score = 100
        elif pixel_std >= self.CONTRAST_THRESHOLD_MEDIUM:
            score = 50 + 50 * (pixel_std - self.CONTRAST_THRESHOLD_MEDIUM) / (self.CONTRAST_THRESHOLD_HIGH - self.CONTRAST_THRESHOLD_MEDIUM)
        elif pixel_std >= self.CONTRAST_THRESHOLD_LOW:
            score = 25 + 25 * (pixel_std - self.CONTRAST_THRESHOLD_LOW) / (self.CONTRAST_THRESHOLD_MEDIUM - self.CONTRAST_THRESHOLD_LOW)
        else:
            score = max(0, 25 * pixel_std / self.CONTRAST_THRESHOLD_LOW)

        return min(100, score), round(pixel_std, 2)

    def _assess_brightness(self, gray: 'np.ndarray') -> tuple:
        """
        Evalua brillo usando valor medio de pixeles.

        Rango optimo: 80-200 (ni muy oscuro ni muy claro).
        """
        mean_val = np.mean(gray)

        # Score maximo si esta en rango optimo
        if self.BRIGHTNESS_OPTIMAL_MIN <= mean_val <= self.BRIGHTNESS_OPTIMAL_MAX:
            score = 100
        elif mean_val < self.BRIGHTNESS_OPTIMAL_MIN:
            # Muy oscuro
            score = max(0, 100 * mean_val / self.BRIGHTNESS_OPTIMAL_MIN)
        else:
            # Muy claro
            excess = mean_val - self.BRIGHTNESS_OPTIMAL_MAX
            max_excess = 255 - self.BRIGHTNESS_OPTIMAL_MAX
            score = max(0, 100 - 100 * excess / max_excess)

        return score, round(mean_val, 2)

    def _assess_resolution(self, img: 'np.ndarray') -> tuple:
        """
        Evalua resolucion basado en dimensiones minimas.

        Claude Vision necesita minimo 200px. Optimo >500px.
        """
        height, width = img.shape[:2]
        min_dim = min(height, width)

        if min_dim >= self.GOOD_RESOLUTION:
            score = 100
        elif min_dim >= self.MIN_RESOLUTION:
            score = 50 + 50 * (min_dim - self.MIN_RESOLUTION) / (self.GOOD_RESOLUTION - self.MIN_RESOLUTION)
        else:
            score = max(0, 50 * min_dim / self.MIN_RESOLUTION)

        return score, {"width": width, "height": height, "min": min_dim}

    def _calculate_overall_level(self, report: QualityReport) -> QualityLevel:
        """
        Calcula nivel general basado en scores individuales.

        Logica:
        - Si algun score es critico (<25), nivel baja
        - Promedio ponderado determina nivel final
        """
        scores = [
            report.blur_score,
            report.contrast_score,
            report.brightness_score,
            report.resolution_score
        ]

        min_score = min(scores)
        avg_score = sum(scores) / len(scores)

        # Si alguna metrica es muy mala, no puede ser HIGH
        if min_score < 25:
            if avg_score < 40:
                return QualityLevel.REJECT
            return QualityLevel.LOW

        # Basado en promedio
        if avg_score >= 70:
            return QualityLevel.HIGH
        elif avg_score >= 45:
            return QualityLevel.MEDIUM
        elif avg_score >= 25:
            return QualityLevel.LOW
        else:
            return QualityLevel.REJECT

    def _generate_recommendations(self, report: QualityReport) -> List[str]:
        """Genera recomendaciones basadas en scores."""
        recommendations = []

        if report.blur_score < 50:
            if report.blur_score < 25:
                recommendations.append("Imagen muy borrosa. Tome una nueva foto mas nitida.")
            else:
                recommendations.append("Imagen algo borrosa. Se aplicara mejora de nitidez.")

        if report.contrast_score < 50:
            if report.contrast_score < 25:
                recommendations.append("Muy bajo contraste. Use mejor iluminacion.")
            else:
                recommendations.append("Bajo contraste. Se aplicara CLAHE.")

        if report.brightness_score < 50:
            raw_brightness = report.raw_metrics.get("mean_brightness", 128)
            if raw_brightness < self.BRIGHTNESS_OPTIMAL_MIN:
                recommendations.append("Imagen muy oscura. Mejore la iluminacion.")
            else:
                recommendations.append("Imagen muy clara/sobreexpuesta.")

        if report.resolution_score < 50:
            dims = report.raw_metrics.get("dimensions", {})
            if dims.get("min", 0) < self.MIN_RESOLUTION:
                recommendations.append(f"Resolucion muy baja ({dims.get('min', 0)}px). Minimo recomendado: {self.MIN_RESOLUTION}px.")

        if report.overall_level == QualityLevel.HIGH:
            recommendations.append("Calidad optima. Sin preprocesamiento necesario.")
        elif report.overall_level == QualityLevel.REJECT:
            recommendations.append("Calidad insuficiente. Por favor proporcione una mejor imagen.")

        return recommendations


# Singleton
_quality_service: Optional[DocumentQualityService] = None


def get_document_quality_service() -> DocumentQualityService:
    """Factory para obtener instancia singleton del servicio"""
    global _quality_service
    if _quality_service is None:
        _quality_service = DocumentQualityService()
    return _quality_service
