"""
Test de preprocesamiento WhatsApp
Verifica las mejoras de OCR para imágenes de documentos enviados por WhatsApp.

Uso:
    cd controlnot-v2/backend
    python -m pytest tests/test_whatsapp_preprocessing.py -v

    # O ejecutar directamente para prueba visual:
    python tests/test_whatsapp_preprocessing.py
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.image_preprocessing_service import (
    ImagePreprocessingService,
    get_image_preprocessing_service
)


# Ruta a imágenes de prueba
TEST_IMAGES_PATH = Path(__file__).parent.parent.parent.parent / "pruebas" / "DONACION" / "EJEMPLO3"


def test_orientation_detection():
    """Test: Detecta imágenes rotadas 90°"""
    service = get_image_preprocessing_service()

    # Cargar una imagen de prueba
    donador_path = TEST_IMAGES_PATH / "DONADOR"
    if not donador_path.exists():
        print(f"SKIP: Ruta no encontrada: {donador_path}")
        return

    images = list(donador_path.glob("*.jpeg"))
    if not images:
        print(f"SKIP: No hay imágenes JPEG en {donador_path}")
        return

    for img_path in images[:2]:  # Probar solo 2
        print(f"\nProbando: {img_path.name}")

        with open(img_path, 'rb') as f:
            content = f.read()

        corrected, rotation = service.detect_and_correct_orientation(content)

        print(f"  - Tamaño original: {len(content):,} bytes")
        print(f"  - Rotación detectada: {rotation}°")
        print(f"  - Tamaño corregido: {len(corrected):,} bytes")

        # Guardar imagen corregida para inspección visual
        output_path = img_path.parent / f"_corrected_{img_path.name}"
        with open(output_path, 'wb') as f:
            f.write(corrected)
        print(f"  - Guardado: {output_path.name}")


def test_document_cropping():
    """Test: Recorta documento eliminando fondo"""
    service = get_image_preprocessing_service()

    donador_path = TEST_IMAGES_PATH / "DONADOR"
    if not donador_path.exists():
        print(f"SKIP: Ruta no encontrada: {donador_path}")
        return

    images = list(donador_path.glob("*.jpeg"))
    if not images:
        print(f"SKIP: No hay imágenes JPEG en {donador_path}")
        return

    for img_path in images[:2]:
        print(f"\nProbando recorte: {img_path.name}")

        with open(img_path, 'rb') as f:
            content = f.read()

        cropped, metadata = service.detect_and_crop_document(content)

        print(f"  - Recortado: {metadata.get('cropped', False)}")
        if metadata.get('cropped'):
            print(f"  - Tamaño original: {metadata.get('original_size')}")
            print(f"  - Tamaño recortado: {metadata.get('cropped_size')}")
            print(f"  - Área ratio: {metadata.get('area_ratio')}")
            print(f"  - Rectangularidad: {metadata.get('rectangularity')}")

            output_path = img_path.parent / f"_cropped_{img_path.name}"
            with open(output_path, 'wb') as f:
                f.write(cropped)
            print(f"  - Guardado: {output_path.name}")
        else:
            print(f"  - Razón: {metadata.get('reason', 'desconocida')}")


def test_multiple_document_segmentation():
    """Test: Segmenta múltiples documentos (2 INEs) en una foto"""
    service = get_image_preprocessing_service()

    donador_path = TEST_IMAGES_PATH / "DONADOR"
    if not donador_path.exists():
        print(f"SKIP: Ruta no encontrada: {donador_path}")
        return

    images = list(donador_path.glob("*.jpeg"))
    if not images:
        print(f"SKIP: No hay imágenes JPEG en {donador_path}")
        return

    # Probar con la primera imagen
    img_path = images[0]
    print(f"\nProbando segmentación: {img_path.name}")

    with open(img_path, 'rb') as f:
        content = f.read()

    segments = service.segment_multiple_documents(content)

    print(f"  - Documentos encontrados: {len(segments)}")

    for i, (segment_content, metadata) in enumerate(segments):
        print(f"\n  Documento {i+1}:")
        print(f"    - Segmentado: {metadata.get('segmented', False)}")
        print(f"    - Área ratio: {metadata.get('area_ratio', 'N/A')}")

        output_path = img_path.parent / f"_segment{i+1}_{img_path.name}"
        with open(output_path, 'wb') as f:
            f.write(segment_content)
        print(f"    - Guardado: {output_path.name}")


def test_whatsapp_pipeline():
    """Test: Pipeline completo para WhatsApp"""
    service = get_image_preprocessing_service()

    donador_path = TEST_IMAGES_PATH / "DONADOR"
    if not donador_path.exists():
        print(f"SKIP: Ruta no encontrada: {donador_path}")
        return

    images = list(donador_path.glob("*.jpeg"))
    if not images:
        print(f"SKIP: No hay imágenes JPEG en {donador_path}")
        return

    for img_path in images[:3]:
        print(f"\nPipeline WhatsApp: {img_path.name}")

        with open(img_path, 'rb') as f:
            content = f.read()

        processed, media_type, metadata = service.preprocess_whatsapp_image(
            content,
            img_path.name,
            auto_rotate=True,
            auto_crop=True,
            auto_segment=False
        )

        print(f"  - Pasos aplicados: {metadata.get('steps_applied', [])}")
        print(f"  - Tamaño original: {metadata.get('original_size', 0):,} bytes")
        print(f"  - Tamaño final: {metadata.get('final_size', 0):,} bytes")
        print(f"  - Reducción: {metadata.get('size_reduction_percent', 0)}%")

        if 'rotation_applied' in metadata:
            print(f"  - Rotación aplicada: {metadata['rotation_applied']}°")

        if 'crop_info' in metadata:
            print(f"  - Recorte info: {metadata['crop_info']}")

        output_path = img_path.parent / f"_whatsapp_processed_{img_path.name}"
        with open(output_path, 'wb') as f:
            f.write(processed)
        print(f"  - Guardado: {output_path.name}")


def main():
    """Ejecutar todas las pruebas"""
    print("=" * 60)
    print("TEST DE PREPROCESAMIENTO WHATSAPP")
    print("=" * 60)

    print(f"\nRuta de imágenes: {TEST_IMAGES_PATH}")
    print(f"Existe: {TEST_IMAGES_PATH.exists()}")

    if not TEST_IMAGES_PATH.exists():
        print("\nERROR: La ruta de pruebas no existe")
        return

    print("\n" + "=" * 60)
    print("1. TEST DE DETECCIÓN DE ORIENTACIÓN")
    print("=" * 60)
    test_orientation_detection()

    print("\n" + "=" * 60)
    print("2. TEST DE RECORTE DE DOCUMENTO")
    print("=" * 60)
    test_document_cropping()

    print("\n" + "=" * 60)
    print("3. TEST DE SEGMENTACIÓN DE MÚLTIPLES DOCUMENTOS")
    print("=" * 60)
    test_multiple_document_segmentation()

    print("\n" + "=" * 60)
    print("4. TEST DE PIPELINE WHATSAPP COMPLETO")
    print("=" * 60)
    test_whatsapp_pipeline()

    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("\nRevisa las imágenes con prefijo '_' en las carpetas de prueba")
    print("para verificar visualmente los resultados.")


if __name__ == "__main__":
    main()
