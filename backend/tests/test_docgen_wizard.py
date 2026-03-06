"""
Tests for the enhanced DocGen Wizard (progressive storage, evaluation, completeness report, merge).
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.wa_menu_handlers import WAMenuHandler
from app.services.wa_docgen_service import WADocgenService


# ── Unit tests: merge_extracted_data ──

class TestMergeExtractedData:
    def setup_method(self):
        self.svc = WADocgenService()

    def test_new_field_added(self):
        existing = {"Nombre": "Juan"}
        new_data = {"Apellido": "Perez"}
        result = self.svc.merge_extracted_data(existing, new_data)
        assert result == {"Nombre": "Juan", "Apellido": "Perez"}

    def test_no_encontrado_replaced(self):
        existing = {"Nombre": "Juan", "CURP": "NO ENCONTRADO"}
        new_data = {"CURP": "XXXX000000HDFRRN09"}
        result = self.svc.merge_extracted_data(existing, new_data)
        assert result["CURP"] == "XXXX000000HDFRRN09"

    def test_existing_value_preserved(self):
        existing = {"Nombre": "Juan"}
        new_data = {"Nombre": "Pedro"}
        result = self.svc.merge_extracted_data(existing, new_data)
        assert result["Nombre"] == "Juan"

    def test_no_encontrado_not_replaced_by_no_encontrado(self):
        existing = {"CURP": "NO ENCONTRADO"}
        new_data = {"CURP": "NO ENCONTRADO"}
        result = self.svc.merge_extracted_data(existing, new_data)
        assert result["CURP"] == "NO ENCONTRADO"

    def test_empty_existing(self):
        result = self.svc.merge_extracted_data({}, {"A": "1", "B": "2"})
        assert result == {"A": "1", "B": "2"}

    def test_empty_new(self):
        result = self.svc.merge_extracted_data({"A": "1"}, {})
        assert result == {"A": "1"}

    def test_mixed_scenario(self):
        existing = {
            "Vendedor": "RAUL CERVANTES",
            "Comprador": "NO ENCONTRADO",
            "Valor": "$1,250,000",
            "RFC_Vendedor": "NO ENCONTRADO",
        }
        new_data = {
            "Comprador": "MARCO GARCIA",
            "RFC_Vendedor": "CEAM800101XXX",
            "Superficie": "250 m2",
            "Vendedor": "OTRO NOMBRE",  # should NOT replace
        }
        result = self.svc.merge_extracted_data(existing, new_data)
        assert result["Vendedor"] == "RAUL CERVANTES"
        assert result["Comprador"] == "MARCO GARCIA"
        assert result["RFC_Vendedor"] == "CEAM800101XXX"
        assert result["Superficie"] == "250 m2"
        assert result["Valor"] == "$1,250,000"


# ── Unit tests: get_field_sources ──

class TestGetFieldSources:
    def setup_method(self):
        self.svc = WADocgenService()

    def test_compraventa_has_sources(self):
        sources = self.svc.get_field_sources('compraventa')
        # Should return a dict, may have some fields with source
        assert isinstance(sources, dict)

    def test_unknown_type_returns_empty(self):
        sources = self.svc.get_field_sources('tipo_inexistente')
        assert sources == {}

    def test_all_doc_types(self):
        from app.services.wa_docgen_service import DOC_TYPES
        for doc_type in DOC_TYPES:
            sources = self.svc.get_field_sources(doc_type)
            assert isinstance(sources, dict)


# ── Unit tests: _format_completeness_report ──

class TestFormatCompletenessReport:
    def setup_method(self):
        self.handler = WAMenuHandler()

    def test_basic_report(self):
        extracted = {
            "Vendedor": "RAUL CERVANTES",
            "Comprador": "MARCO GARCIA",
            "Valor": "$1,250,000",
            "CURP_Vendedor": "NO ENCONTRADO",
        }
        validation = {
            "completeness": 0.75,
            "total_fields": 4,
            "found_fields": 3,
            "critical_missing": ["CURP_Vendedor"],
            "optional_missing": [],
        }
        field_sources = {"CURP_Vendedor": "Constancia CURP"}

        report = self.handler._format_completeness_report(extracted, validation, field_sources)

        assert "75%" in report
        assert "RAUL CERVANTES" in report
        assert "Curp Vendedor" in report
        assert "Constancia CURP" in report

    def test_100_percent(self):
        extracted = {"Campo1": "Valor1"}
        validation = {
            "completeness": 1.0,
            "total_fields": 1,
            "found_fields": 1,
            "critical_missing": [],
            "optional_missing": [],
        }
        report = self.handler._format_completeness_report(extracted, validation, {})
        assert "100%" in report
        assert "faltantes criticos" not in report

    def test_with_optional_missing(self):
        extracted = {"Campo1": "Valor1", "Opcional1": "NO ENCONTRADO"}
        validation = {
            "completeness": 0.5,
            "total_fields": 2,
            "found_fields": 1,
            "critical_missing": [],
            "optional_missing": ["Opcional1"],
        }
        report = self.handler._format_completeness_report(extracted, validation, {})
        assert "Opcionales faltantes" in report

    def test_tip_shows_sources(self):
        extracted = {}
        validation = {
            "completeness": 0.0,
            "total_fields": 2,
            "found_fields": 0,
            "critical_missing": ["campo_a", "campo_b"],
            "optional_missing": [],
        }
        field_sources = {
            "campo_a": "Boleta RPP",
            "campo_b": "Certificado Catastral",
        }
        report = self.handler._format_completeness_report(extracted, validation, field_sources)
        assert "Tip:" in report
        assert "Boleta RPP" in report


# ── Integration-style tests with mocks: collect_images flow ──

class TestDocgenCollectImagesFlow:
    def setup_method(self):
        self.handler = WAMenuHandler()
        self.tenant_id = uuid4()
        self.phone = '5211111111'
        self.staff = {'display_name': 'Test', 'user_id': str(uuid4())}

    @pytest.mark.asyncio
    async def test_image_received_stores_and_evaluates(self):
        """When an image is received, it should store progressively and evaluate."""
        session = {
            'menu': 'generate_doc',
            'docgen_step': 'collect_images',
            'docgen_type': 'compraventa',
            'docgen_images': [],
            'docgen_prev_image_count': 0,
        }

        mock_store_result = {
            'storage_path': 'tenant/whatsapp/docgen_521/img_0_abc.jpg',
            'content_bytes': b'fake_image_bytes',
            'mime_type': 'image/jpeg',
        }
        mock_eval_result = {
            'readable': 'si',
            'document_type': 'INE',
            'quality': 'Buena',
            'fields_contributed': ['Nombre', 'CURP', 'Domicilio'],
        }

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock) as mock_save, \
             patch('app.services.wa_docgen_service.whatsapp_service'), \
             patch.object(WADocgenService, 'store_image_progressively', new_callable=AsyncMock, return_value=mock_store_result), \
             patch.object(WADocgenService, 'evaluate_image_quick', new_callable=AsyncMock, return_value=mock_eval_result):

            mock_wa.send_text = AsyncMock()
            mock_wa.send_interactive_buttons = AsyncMock()

            await self.handler._docgen_collect_images(
                tenant_id=self.tenant_id,
                phone=self.phone,
                staff=self.staff,
                user_input={'type': 'media', 'media_id': 'meta_media_123', 'id': '', 'text': ''},
                session=session,
            )

            # Should have sent feedback text
            mock_wa.send_text.assert_called_once()
            feedback_text = mock_wa.send_text.call_args[0][1]
            assert "INE" in feedback_text
            assert "Buena" in feedback_text

            # Session should have 1 image record
            saved_session = mock_save.call_args[0][2]
            assert len(saved_session['docgen_images']) == 1
            assert saved_session['docgen_images'][0]['storage_path'] == 'tenant/whatsapp/docgen_521/img_0_abc.jpg'

    @pytest.mark.asyncio
    async def test_bad_quality_image_shows_warning(self):
        """When image quality is Mala, should show warning with suggestion."""
        session = {
            'menu': 'generate_doc',
            'docgen_step': 'collect_images',
            'docgen_type': 'compraventa',
            'docgen_images': [],
            'docgen_prev_image_count': 0,
        }

        mock_store_result = {
            'storage_path': 'tenant/whatsapp/docgen_521/img_0_abc.jpg',
            'content_bytes': b'blurry',
            'mime_type': 'image/jpeg',
        }
        mock_eval_result = {
            'readable': 'no',
            'document_type': 'Otro',
            'quality': 'Mala',
            'fields_contributed': [],
        }

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock), \
             patch('app.services.wa_docgen_service.whatsapp_service'), \
             patch.object(WADocgenService, 'store_image_progressively', new_callable=AsyncMock, return_value=mock_store_result), \
             patch.object(WADocgenService, 'evaluate_image_quick', new_callable=AsyncMock, return_value=mock_eval_result):

            mock_wa.send_text = AsyncMock()
            mock_wa.send_interactive_buttons = AsyncMock()

            await self.handler._docgen_collect_images(
                tenant_id=self.tenant_id,
                phone=self.phone,
                staff=self.staff,
                user_input={'type': 'media', 'media_id': 'meta_media_456', 'id': '', 'text': ''},
                session=session,
            )

            feedback_text = mock_wa.send_text.call_args[0][1]
            assert "problemas" in feedback_text
            assert "iluminacion" in feedback_text

    @pytest.mark.asyncio
    async def test_listo_triggers_extraction_and_completeness(self):
        """Pressing 'Listo' should extract, validate, and show completeness report."""
        session = {
            'menu': 'generate_doc',
            'docgen_step': 'collect_images',
            'docgen_type': 'compraventa',
            'docgen_template_id': str(uuid4()),
            'docgen_images': [
                {'storage_path': 'tenant/whatsapp/docgen_521/img_0_abc.jpg', 'mime_type': 'image/jpeg'},
            ],
            'docgen_prev_image_count': 0,
        }

        mock_downloaded = [{'content': 'base64data', 'media_type': 'image/jpeg', 'source_type': 'base64'}]
        mock_extracted = {"Vendedor": "RAUL", "Comprador": "NO ENCONTRADO"}
        mock_validation = {
            "completeness": 0.5,
            "total_fields": 2,
            "found_fields": 1,
            "critical_missing": ["Comprador"],
            "optional_missing": [],
        }

        mock_extraction_svc = MagicMock()
        mock_extraction_svc.validate_extracted_data.return_value = mock_validation

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock) as mock_save, \
             patch.object(WADocgenService, 'load_stored_images', new_callable=AsyncMock, return_value=mock_downloaded), \
             patch.object(WADocgenService, 'extract_from_images', new_callable=AsyncMock, return_value=mock_extracted), \
             patch.object(WADocgenService, 'get_field_sources', return_value={}), \
             patch('app.services.anthropic_service.AnthropicExtractionService', return_value=mock_extraction_svc):

            mock_wa.send_text = AsyncMock()
            mock_wa.send_interactive_buttons = AsyncMock()

            await self.handler._docgen_collect_images(
                tenant_id=self.tenant_id,
                phone=self.phone,
                staff=self.staff,
                user_input={'type': '', 'media_id': '', 'id': 'docgen_done_images', 'text': ''},
                session=session,
            )

            # Should show completeness report
            report_call = mock_wa.send_text.call_args_list[-1]
            report_text = report_call[0][1]
            assert "50%" in report_text

            # Should show 3 buttons
            buttons_call = mock_wa.send_interactive_buttons.call_args
            buttons = buttons_call[1]['buttons']
            button_ids = [b['id'] for b in buttons]
            assert 'docgen_generate_anyway' in button_ids
            assert 'docgen_add_more' in button_ids
            assert 'docgen_cancel' in button_ids

            # Session should be at completeness_report step
            saved = mock_save.call_args[0][2]
            assert saved['docgen_step'] == 'completeness_report'


# ── Completeness report handler tests ──

class TestDocgenCompletenessReport:
    def setup_method(self):
        self.handler = WAMenuHandler()
        self.tenant_id = uuid4()
        self.phone = '5211111111'
        self.staff = {'display_name': 'Test', 'user_id': str(uuid4())}
        self.base_session = {
            'menu': 'generate_doc',
            'docgen_step': 'completeness_report',
            'docgen_type': 'compraventa',
            'docgen_template_id': str(uuid4()),
            'docgen_extracted': {"Vendedor": "RAUL"},
            'docgen_images': [{'storage_path': 'x', 'mime_type': 'image/jpeg'}],
            'docgen_prev_image_count': 1,
        }

    @pytest.mark.asyncio
    async def test_cancel_clears_session(self):
        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock) as mock_save, \
             patch.object(self.handler, '_show_main_menu', new_callable=AsyncMock):

            mock_wa.send_text = AsyncMock()

            await self.handler._docgen_completeness_report(
                self.tenant_id, self.phone, self.staff,
                {'id': 'docgen_cancel', 'text': ''},
                dict(self.base_session),
            )

            mock_save.assert_called_with(self.tenant_id, self.phone, {})

    @pytest.mark.asyncio
    async def test_add_more_goes_back_to_collect(self):
        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock) as mock_save:

            mock_wa.send_text = AsyncMock()
            mock_wa.send_interactive_buttons = AsyncMock()

            await self.handler._docgen_completeness_report(
                self.tenant_id, self.phone, self.staff,
                {'id': 'docgen_add_more', 'text': ''},
                dict(self.base_session),
            )

            saved = mock_save.call_args[0][2]
            assert saved['docgen_step'] == 'collect_images'
            # docgen_extracted should be preserved
            assert saved['docgen_extracted'] == {"Vendedor": "RAUL"}

    @pytest.mark.asyncio
    async def test_generate_anyway_creates_document(self):
        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock), \
             patch.object(self.handler, '_show_main_menu', new_callable=AsyncMock), \
             patch.object(WADocgenService, 'generate_and_store', new_callable=AsyncMock) as mock_gen, \
             patch.object(WADocgenService, 'send_document_via_whatsapp', new_callable=AsyncMock, return_value=True):

            mock_wa.send_text = AsyncMock()
            mock_gen.return_value = {
                'storage_path': 'docs/output.docx',
                'nombre_documento': 'compraventa.docx',
            }

            await self.handler._docgen_completeness_report(
                self.tenant_id, self.phone, self.staff,
                {'id': 'docgen_generate_anyway', 'text': ''},
                dict(self.base_session),
            )

            mock_gen.assert_called_once()
            # Should have sent success message
            texts = [call[0][1] for call in mock_wa.send_text.call_args_list]
            assert any("exitosamente" in t for t in texts)


# ── Add-more-photos merge flow ──

class TestAddMorePhotosMerge:
    def setup_method(self):
        self.handler = WAMenuHandler()
        self.tenant_id = uuid4()
        self.phone = '5211111111'
        self.staff = {'display_name': 'Test', 'user_id': str(uuid4())}

    @pytest.mark.asyncio
    async def test_listo_with_prev_data_merges(self):
        """When prev_image_count > 0, new extraction should merge with existing."""
        session = {
            'menu': 'generate_doc',
            'docgen_step': 'collect_images',
            'docgen_type': 'compraventa',
            'docgen_template_id': str(uuid4()),
            'docgen_images': [
                {'storage_path': 'old.jpg', 'mime_type': 'image/jpeg'},
                {'storage_path': 'new.jpg', 'mime_type': 'image/jpeg'},
            ],
            'docgen_prev_image_count': 1,  # Only index 1+ is new
            'docgen_extracted': {"Vendedor": "RAUL", "CURP": "NO ENCONTRADO"},
        }

        mock_downloaded = [{'content': 'b64', 'media_type': 'image/jpeg', 'source_type': 'base64'}]
        mock_new_extracted = {"CURP": "XXXX000000", "Superficie": "250 m2"}
        mock_validation = {
            "completeness": 0.9,
            "total_fields": 3,
            "found_fields": 3,
            "critical_missing": [],
            "optional_missing": [],
        }

        mock_extraction_svc = MagicMock()
        mock_extraction_svc.validate_extracted_data.return_value = mock_validation

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock) as mock_save, \
             patch.object(WADocgenService, 'load_stored_images', new_callable=AsyncMock, return_value=mock_downloaded) as mock_load, \
             patch.object(WADocgenService, 'extract_from_images', new_callable=AsyncMock, return_value=mock_new_extracted), \
             patch.object(WADocgenService, 'get_field_sources', return_value={}), \
             patch('app.services.anthropic_service.AnthropicExtractionService', return_value=mock_extraction_svc):

            mock_wa.send_text = AsyncMock()
            mock_wa.send_interactive_buttons = AsyncMock()

            await self.handler._docgen_collect_images(
                tenant_id=self.tenant_id,
                phone=self.phone,
                staff=self.staff,
                user_input={'type': '', 'media_id': '', 'id': 'docgen_done_images', 'text': ''},
                session=session,
            )

            # load_stored_images should only get the NEW image (index 1)
            loaded_records = mock_load.call_args[0][0]
            assert len(loaded_records) == 1
            assert loaded_records[0]['storage_path'] == 'new.jpg'

            # Merged data should have CURP replaced and Superficie added
            saved = mock_save.call_args[0][2]
            merged = saved['docgen_extracted']
            assert merged['Vendedor'] == 'RAUL'
            assert merged['CURP'] == 'XXXX000000'
            assert merged['Superficie'] == '250 m2'
