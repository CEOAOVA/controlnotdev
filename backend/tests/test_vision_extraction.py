"""
Tests para extraccion con Claude Vision

Verifica:
1. Modelos INE, Pasaporte, CURP
2. ImagePreprocessingService
3. Validaciones INE
4. MODEL_MAP con identificaciones
"""
import pytest
from unittest.mock import MagicMock, patch
import io

# Modelos
from app.models.ine import INECredencial
from app.models.pasaporte import PasaporteMexicano
from app.models.curp_constancia import ConstanciaCURP

# Servicios
from app.services.image_preprocessing_service import (
    ImagePreprocessingService,
    get_image_preprocessing_service,
    PILLOW_AVAILABLE
)
from app.services.anthropic_service import AnthropicExtractionService

# Validadores
from app.utils.validators import NotarialValidator, ValidationType


class TestINEModel:
    """Tests para el modelo INECredencial"""

    def test_ine_model_has_all_fields(self):
        """Verifica que el modelo tenga todos los campos esperados"""
        expected_fields = [
            'nombre_completo',
            'clave_elector',
            'curp',
            'fecha_nacimiento',
            'sexo',
            'domicilio',
            'seccion_electoral',
            'estado',
            'municipio',
            'vigencia',
            'numero_vertical',
            'numero_ocr',
            'emision'
        ]

        model_fields = INECredencial.model_fields.keys()

        for field in expected_fields:
            assert field in model_fields, f"Campo {field} falta en INECredencial"

    def test_ine_model_accepts_partial_data(self):
        """Verifica que el modelo acepta datos parciales (Optional)"""
        ine = INECredencial(
            nombre_completo="CERVANTES AREVALO RAUL",
            curp="CEAR640813HMNRRL02"
        )

        assert ine.nombre_completo == "CERVANTES AREVALO RAUL"
        assert ine.curp == "CEAR640813HMNRRL02"
        assert ine.clave_elector is None  # Optional field

    def test_ine_model_example_is_valid(self):
        """Verifica que el ejemplo del modelo sea valido"""
        example = INECredencial.Config.json_schema_extra['example']
        ine = INECredencial(**example)

        assert ine.nombre_completo == "CERVANTES AREVALO RAUL"
        assert ine.curp == "CEAR640813HMNRRL02"
        assert ine.clave_elector == "CRVRAL64081314H100"


class TestPasaporteModel:
    """Tests para el modelo PasaporteMexicano"""

    def test_pasaporte_model_has_all_fields(self):
        """Verifica que el modelo tenga todos los campos esperados"""
        expected_fields = [
            'nombre_completo',
            'apellidos',
            'nombres',
            'nacionalidad',
            'fecha_nacimiento',
            'sexo',
            'lugar_nacimiento',
            'curp',
            'numero_pasaporte',
            'fecha_expedicion',
            'fecha_vencimiento',
            'autoridad_expedidora',
            'mrz_linea1',
            'mrz_linea2'
        ]

        model_fields = PasaporteMexicano.model_fields.keys()

        for field in expected_fields:
            assert field in model_fields, f"Campo {field} falta en PasaporteMexicano"

    def test_pasaporte_model_example_is_valid(self):
        """Verifica que el ejemplo del modelo sea valido"""
        example = PasaporteMexicano.Config.json_schema_extra['example']
        pasaporte = PasaporteMexicano(**example)

        assert pasaporte.numero_pasaporte == "G12345678"
        assert pasaporte.nacionalidad == "MEXICANA"


class TestConstanciaCURPModel:
    """Tests para el modelo ConstanciaCURP"""

    def test_curp_model_has_all_fields(self):
        """Verifica que el modelo tenga todos los campos esperados"""
        expected_fields = [
            'curp',
            'nombre_completo',
            'primer_apellido',
            'segundo_apellido',
            'nombres',
            'fecha_nacimiento',
            'sexo',
            'entidad_nacimiento',
            'nacionalidad',
            'fecha_registro',
            'clave_entidad_registro',
            'folio',
            'codigo_verificacion'
        ]

        model_fields = ConstanciaCURP.model_fields.keys()

        for field in expected_fields:
            assert field in model_fields, f"Campo {field} falta en ConstanciaCURP"


class TestImagePreprocessingService:
    """Tests para ImagePreprocessingService"""

    def test_service_can_be_instantiated(self):
        """Verifica que el servicio se pueda instanciar"""
        service = ImagePreprocessingService()
        assert service is not None
        assert service.max_dimension == 1568

    def test_singleton_returns_same_instance(self):
        """Verifica el patron singleton"""
        service1 = get_image_preprocessing_service()
        service2 = get_image_preprocessing_service()
        assert service1 is service2

    def test_detect_media_type_from_extension(self):
        """Verifica deteccion de media type por extension"""
        service = ImagePreprocessingService()

        assert service._detect_media_type("foto.jpg") == "image/jpeg"
        assert service._detect_media_type("foto.jpeg") == "image/jpeg"
        assert service._detect_media_type("foto.png") == "image/png"
        assert service._detect_media_type("foto.gif") == "image/gif"
        assert service._detect_media_type("foto.webp") == "image/webp"
        assert service._detect_media_type("foto.unknown") == "image/jpeg"  # default

    @pytest.mark.skipif(not PILLOW_AVAILABLE, reason="Pillow not installed")
    def test_preprocess_returns_jpeg(self):
        """Verifica que siempre retorne JPEG"""
        # Crear imagen de prueba simple (1x1 pixel PNG)
        from PIL import Image

        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        png_content = buffer.getvalue()

        service = ImagePreprocessingService()
        result, media_type = service.preprocess(png_content, "test.png")

        assert media_type == "image/jpeg"
        # Verificar que el resultado empieza con la firma JPEG
        assert result[:3] == b'\xff\xd8\xff'


class TestMODELMAP:
    """Tests para verificar que MODEL_MAP incluye identificaciones"""

    def test_model_map_includes_ine(self):
        """Verifica que ine_ife este en MODEL_MAP"""
        assert "ine_ife" in AnthropicExtractionService.MODEL_MAP
        assert AnthropicExtractionService.MODEL_MAP["ine_ife"] == INECredencial

    def test_model_map_includes_pasaporte(self):
        """Verifica que pasaporte este en MODEL_MAP"""
        assert "pasaporte" in AnthropicExtractionService.MODEL_MAP
        assert AnthropicExtractionService.MODEL_MAP["pasaporte"] == PasaporteMexicano

    def test_model_map_includes_curp_constancia(self):
        """Verifica que curp_constancia este en MODEL_MAP"""
        assert "curp_constancia" in AnthropicExtractionService.MODEL_MAP
        assert AnthropicExtractionService.MODEL_MAP["curp_constancia"] == ConstanciaCURP


class TestINEValidations:
    """Tests para validaciones especificas de INE"""

    def test_validate_clave_elector_valid(self):
        """Verifica validacion de clave de elector valida"""
        validator = NotarialValidator()
        result = validator.validate_clave_elector("CRVRAL64081314H100")

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.value == "CRVRAL64081314H100"

    def test_validate_clave_elector_invalid_length(self):
        """Verifica error por longitud incorrecta"""
        validator = NotarialValidator()
        result = validator.validate_clave_elector("CRVRAL")

        assert not result.is_valid
        assert any("18 caracteres" in e for e in result.errors)

    def test_validate_clave_elector_invalid_format(self):
        """Verifica error por formato incorrecto"""
        validator = NotarialValidator()
        result = validator.validate_clave_elector("123456789012345678")

        assert not result.is_valid
        assert any("Formato" in e for e in result.errors)

    def test_validate_clave_elector_empty(self):
        """Verifica manejo de clave vacia"""
        validator = NotarialValidator()
        result = validator.validate_clave_elector("")

        assert not result.is_valid
        assert any("vacia" in e for e in result.errors)

    def test_validate_seccion_electoral_valid(self):
        """Verifica validacion de seccion electoral valida"""
        validator = NotarialValidator()
        result = validator.validate_seccion_electoral("1234")

        assert result.is_valid
        assert result.value == "1234"

    def test_validate_seccion_electoral_pads_zeros(self):
        """Verifica que normaliza con ceros a la izquierda"""
        validator = NotarialValidator()
        result = validator.validate_seccion_electoral("123")

        # Debe fallar por longitud pero normaliza
        assert not result.is_valid  # 3 digitos != 4
        assert "4 digitos" in result.errors[0]

    def test_validate_ine_data_full(self):
        """Verifica validacion de datos INE completos"""
        validator = NotarialValidator()

        data = {
            "curp": "CEAR640813HMNRRL02",
            "clave_elector": "CRVRAL64081314H100",
            "fecha_nacimiento": "13/08/1964",
            "seccion_electoral": "1234",
            "sexo": "H"
        }

        results = validator.validate_ine_data(data)

        # Todos deben ser validos
        assert results['curp'].is_valid
        assert results['clave_elector'].is_valid
        assert results['fecha_nacimiento'].is_valid
        assert results['seccion_electoral'].is_valid

    def test_validate_ine_data_sexo_consistency(self):
        """Verifica consistencia entre sexo declarado y CURP"""
        validator = NotarialValidator()

        # Sexo declarado no coincide con CURP (H en CURP, M declarado)
        data = {
            "curp": "CEAR640813HMNRRL02",  # H en posicion 11
            "sexo": "M"  # No coincide
        }

        results = validator.validate_ine_data(data)

        # Debe detectar inconsistencia
        assert 'sexo_consistency' in results
        assert not results['sexo_consistency'].is_valid

    def test_validate_ine_data_skips_no_encontrado(self):
        """Verifica que ignora valores 'NO ENCONTRADO'"""
        validator = NotarialValidator()

        data = {
            "curp": "NO ENCONTRADO",
            "clave_elector": "CRVRAL64081314H100"
        }

        results = validator.validate_ine_data(data)

        # CURP no debe estar en resultados
        assert 'curp' not in results
        # Clave elector si debe estar
        assert 'clave_elector' in results


class TestValidationTypes:
    """Tests para tipos de validacion"""

    def test_validation_type_clave_elector_exists(self):
        """Verifica que exista el tipo CLAVE_ELECTOR"""
        assert ValidationType.CLAVE_ELECTOR.value == "clave_elector"

    def test_validation_type_ine_exists(self):
        """Verifica que exista el tipo INE"""
        assert ValidationType.INE.value == "ine"
