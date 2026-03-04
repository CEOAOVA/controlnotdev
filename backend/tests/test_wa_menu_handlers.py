"""
Tests for WhatsApp Menu Handlers
"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4, UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.wa_menu_handlers import WAMenuHandler, MENU_TRIGGERS


class TestMenuTriggers:
    """Test MENU_TRIGGERS set and reset behavior"""

    def test_menu_triggers(self):
        """'menu', 'hola', 'inicio', '0' all present in MENU_TRIGGERS"""
        for trigger in ['menu', 'hola', 'inicio', '0']:
            assert trigger in MENU_TRIGGERS


class TestHandleDispatch:
    """Test main handle() dispatch logic"""

    def setup_method(self):
        self.handler = WAMenuHandler()
        self.tenant_id = uuid4()
        self.phone = '5211111111'
        self.staff = {'display_name': 'Test', 'user_id': str(uuid4())}

    @pytest.mark.asyncio
    async def test_menu_trigger_resets_session(self):
        """Any MENU_TRIGGER resets session and shows main menu"""
        with patch.object(self.handler, '_save_session', new_callable=AsyncMock) as mock_save, \
             patch.object(self.handler, '_show_main_menu', new_callable=AsyncMock) as mock_menu:
            await self.handler.handle(
                tenant_id=self.tenant_id,
                phone=self.phone,
                staff=self.staff,
                user_input={'text': 'menu', 'id': ''},
                session={'menu': 'case_detail', 'case_id': 'something'},
            )
            mock_save.assert_called_once_with(self.tenant_id, self.phone, {})
            mock_menu.assert_called_once_with(self.phone, self.staff)

    @pytest.mark.asyncio
    async def test_main_menu_dispatches_cases(self):
        """id 'main_cases' → calls _show_cases_list"""
        with patch.object(self.handler, '_show_cases_list', new_callable=AsyncMock) as mock_cases:
            await self.handler.handle(
                tenant_id=self.tenant_id,
                phone=self.phone,
                staff=self.staff,
                user_input={'text': '', 'id': 'main_cases'},
                session={'menu': 'main'},
            )
            mock_cases.assert_called_once()

    @pytest.mark.asyncio
    async def test_case_selection(self):
        """id 'case_{uuid}' → calls _show_case_detail"""
        case_id = uuid4()
        mock_case = {'id': str(case_id), 'case_number': '001', 'status': 'borrador'}

        with patch.object(self.handler, '_show_case_detail', new_callable=AsyncMock) as mock_detail:
            # CaseRepository is imported locally inside _handle_main_menu
            with patch('app.repositories.CaseRepository') as MockCaseRepo:
                instance = MockCaseRepo.return_value
                instance.get_by_id = AsyncMock(return_value=mock_case)

                await self.handler.handle(
                    tenant_id=self.tenant_id,
                    phone=self.phone,
                    staff=self.staff,
                    user_input={'text': '', 'id': f'case_{case_id}'},
                    session={'menu': 'main'},
                )
                mock_detail.assert_called_once()

    @pytest.mark.asyncio
    async def test_transition_flow(self):
        """id 'tr_en_firma' → calls workflow_service.transition"""
        case_id = str(uuid4())
        session = {'menu': 'case_transitions', 'case_id': case_id, 'case_number': '001'}

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_save_session', new_callable=AsyncMock), \
             patch.object(self.handler, '_show_case_detail', new_callable=AsyncMock):

            mock_wa.send_text = AsyncMock()

            with patch('app.services.case_workflow_service.case_workflow_service') as mock_wf:
                mock_wf.transition = AsyncMock(return_value={'status': 'en_firma'})
                mock_wf.get_available_transitions = MagicMock(return_value=[])

                with patch('app.repositories.CaseRepository') as MockCaseRepo:
                    instance = MockCaseRepo.return_value
                    instance.get_by_id = AsyncMock(return_value={
                        'id': case_id, 'case_number': '001', 'status': 'en_firma'
                    })

                    await self.handler._handle_case_transitions(
                        tenant_id=self.tenant_id,
                        phone=self.phone,
                        staff=self.staff,
                        user_input={'id': 'tr_en_firma', 'text': ''},
                        session=session,
                    )

                    mock_wf.transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_checklist_mark(self):
        """id 'cl_{uuid}' → calls checklist_service.update_item_status"""
        case_id = str(uuid4())
        item_id = uuid4()
        session = {'menu': 'case_checklist', 'case_id': case_id, 'case_number': '001'}

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_show_checklist', new_callable=AsyncMock):

            mock_wa.send_text = AsyncMock()

            with patch('app.services.checklist_service.checklist_service') as mock_cl:
                mock_cl.update_item_status = AsyncMock()

                await self.handler._handle_case_checklist(
                    tenant_id=self.tenant_id,
                    phone=self.phone,
                    staff=self.staff,
                    user_input={'id': f'cl_{item_id}', 'text': ''},
                    session=session,
                )

                mock_cl.update_item_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_tramite_complete(self):
        """id 'tm_{uuid}' → calls tramite_service.complete"""
        case_id = str(uuid4())
        tramite_id = uuid4()
        session = {'menu': 'case_tramites', 'case_id': case_id, 'case_number': '001'}

        with patch('app.services.wa_menu_handlers.whatsapp_service') as mock_wa, \
             patch.object(self.handler, '_show_tramites', new_callable=AsyncMock):

            mock_wa.send_text = AsyncMock()

            with patch('app.services.tramite_service.tramite_service') as mock_ts:
                mock_ts.complete = AsyncMock()

                await self.handler._handle_case_tramites(
                    tenant_id=self.tenant_id,
                    phone=self.phone,
                    staff=self.staff,
                    user_input={'id': f'tm_{tramite_id}', 'text': ''},
                    session=session,
                )

                mock_ts.complete.assert_called_once()
