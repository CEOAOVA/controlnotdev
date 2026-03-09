"""
ControlNot v2 - WhatsApp Menu Handlers
Interactive menu system for staff management via WhatsApp.
"""
import asyncio
import traceback
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog

from app.repositories.wa_repository import wa_repository
from app.services.whatsapp_service import whatsapp_service

logger = structlog.get_logger()

# Per-phone locks to serialize image processing and prevent race conditions
_phone_locks: Dict[str, asyncio.Lock] = {}

def _get_phone_lock(tenant_id: UUID, phone: str) -> asyncio.Lock:
    key = f"{tenant_id}:{phone}"
    if key not in _phone_locks:
        _phone_locks[key] = asyncio.Lock()
    return _phone_locks[key]

# Pending photo summary tasks (debounce button spam)
_photo_summary_tasks: Dict[str, asyncio.Task] = {}

# Triggers that reset to main menu
MENU_TRIGGERS = {'menu', 'hola', 'inicio', 'home', '0', 'cancelar'}


class WAMenuHandler:
    """Handles all interactive menu flows for staff WhatsApp sessions."""

    async def handle(
        self,
        tenant_id: UUID,
        phone: str,
        staff: Dict[str, Any],
        user_input: Dict[str, Any],
        session: Dict[str, Any],
    ) -> None:
        """Main dispatch: route to the correct menu handler based on session state."""
        text = user_input.get('text', '')
        input_id = user_input.get('id', '')
        current_menu = session.get('menu', 'main')

        # Global reset triggers
        if text in MENU_TRIGGERS or input_id == 'menu_principal':
            await self._save_session(tenant_id, phone, {})
            await self._show_main_menu(phone, staff)
            return

        # If user selected a main menu option while in a sub-menu, reset to main
        if current_menu != 'main' and input_id.startswith('main_'):
            await self._save_session(tenant_id, phone, {'menu': 'main'})
            current_menu = 'main'

        # Route based on current menu context
        handlers = {
            'main': self._handle_main_menu,
            'case_detail': self._handle_case_detail,
            'case_transitions': self._handle_case_transitions,
            'case_checklist': self._handle_case_checklist,
            'case_tramites': self._handle_case_tramites,
            'case_payments': self._handle_case_payments,
            'search': self._handle_search,
            'notify_select': self._handle_notify_select,
            'alerts': self._handle_alerts,
            'ai': self._handle_ai_chat,
            'generate_doc': self._handle_generate_doc,
        }

        handler = handlers.get(current_menu, self._handle_main_menu)
        await handler(tenant_id, phone, staff, user_input, session)

    # ── Session helpers ──

    async def _save_session(
        self, tenant_id: UUID, phone: str, state: Dict[str, Any]
    ) -> None:
        await wa_repository.update_staff_session(tenant_id, phone, state)

    # ── Main Menu ──

    async def _show_main_menu(
        self, phone: str, staff: Dict[str, Any]
    ) -> None:
        name = staff.get('display_name', 'Usuario')
        await whatsapp_service.send_interactive_list(
            to_phone=phone,
            header="ControlNot",
            body_text=f"Hola {name}, selecciona una opcion:",
            button_text="Ver opciones",
            sections=[{
                "title": "Menu Principal",
                "rows": [
                    {"id": "main_cases", "title": "Mis Expedientes", "description": "Ver casos activos"},
                    {"id": "main_summary", "title": "Resumen del Dia", "description": "Dashboard rapido"},
                    {"id": "main_search", "title": "Buscar Expediente", "description": "Buscar por numero"},
                    {"id": "main_alerts", "title": "Alertas", "description": "Vencidos y urgentes"},
                    {"id": "main_notify", "title": "Notificar Cliente", "description": "Enviar actualizacion"},
                    {"id": "main_ai", "title": "Asistente IA", "description": "Preguntas en lenguaje natural"},
                    {"id": "main_gendoc", "title": "Generar Documento", "description": "Crear escritura desde fotos"},
                ],
            }],
        )

    async def _handle_main_menu(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')
        text = user_input.get('text', '')

        # Handle case selection from list (case_{uuid})
        if input_id.startswith('case_'):
            case_id = input_id.replace('case_', '')
            from app.repositories import CaseRepository
            case = await CaseRepository().get_by_id(UUID(case_id))
            if case:
                await self._show_case_detail(tenant_id, phone, staff, case)
            else:
                await whatsapp_service.send_text(phone, "Expediente no encontrado.")
            return

        if input_id == 'main_cases' or text == '1':
            await self._show_cases_list(tenant_id, phone, staff, session)
        elif input_id == 'main_summary' or text == '2':
            await self._show_daily_summary(tenant_id, phone, staff, session)
        elif input_id == 'main_search' or text == '3':
            await self._save_session(tenant_id, phone, {'menu': 'search'})
            await whatsapp_service.send_text(phone, "Escribe el numero de expediente a buscar:")
        elif input_id == 'main_alerts' or text == '4':
            await self._show_alerts(tenant_id, phone, staff, session)
        elif input_id == 'main_notify' or text == '5':
            await self._show_notify_select(tenant_id, phone, staff, session)
        elif input_id == 'main_ai' or text == '6':
            await self._save_session(tenant_id, phone, {'menu': 'ai'})
            await whatsapp_service.send_text(
                phone,
                "Asistente IA activado. Pregúntame sobre expedientes, clientes, trámites, pagos o calendario.\n\nEscribe 'menu' para volver.",
            )
        elif input_id == 'main_gendoc' or text == '7':
            await self._handle_generate_doc(tenant_id, phone, staff, user_input, {'menu': 'generate_doc', 'docgen_step': 'select_type'})
            return
        else:
            # If it looks like a question/query, route to AI directly
            raw = user_input.get('raw', text)
            if len(raw) > 10 or '?' in raw:
                await self._handle_ai_chat(tenant_id, phone, staff, user_input, session)
            else:
                await self._show_main_menu(phone, staff)

    # ── AI Chat ──

    async def _handle_ai_chat(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        from app.services.wa_admin_ai_service import wa_admin_ai_service
        raw_text = user_input.get('raw', user_input.get('text', '')).strip()
        if not raw_text:
            await whatsapp_service.send_text(phone, "Escribe tu pregunta.")
            return
        await wa_admin_ai_service.handle_message(tenant_id, phone, staff, raw_text, session)

    # ── Cases List ──

    async def _show_cases_list(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        session: Dict[str, Any],
    ) -> None:
        from app.repositories import CaseRepository
        case_repo = CaseRepository()

        # Get active cases (exclude cerrado and cancelado)
        active_statuses = [
            'borrador', 'en_revision', 'checklist_pendiente', 'presupuesto',
            'calculo_impuestos', 'en_firma', 'postfirma', 'tramites_gobierno',
            'inscripcion', 'facturacion', 'entrega',
        ]

        all_cases = []
        for status in active_statuses:
            cases = await case_repo.list_by_status(tenant_id, status, limit=10)
            all_cases.extend(cases)
            if len(all_cases) >= 10:
                break

        all_cases = all_cases[:10]

        if not all_cases:
            await whatsapp_service.send_text(phone, "No hay expedientes activos.")
            await self._show_main_menu(phone, staff)
            return

        from app.services.case_workflow_service import STATUS_LABELS
        rows = []
        for c in all_cases:
            case_num = c.get('case_number', 'S/N')
            status_label = STATUS_LABELS.get(c.get('status', ''), c.get('status', ''))
            doc_type = c.get('document_type', '')
            rows.append({
                "id": f"case_{c['id']}",
                "title": f"{case_num}"[:24],
                "description": f"{doc_type} | {status_label}"[:72],
            })

        await whatsapp_service.send_interactive_list(
            to_phone=phone,
            header="Expedientes Activos",
            body_text=f"Tienes {len(all_cases)} expediente(s) activos:",
            button_text="Ver expedientes",
            sections=[{"title": "Expedientes", "rows": rows}],
        )

        await self._save_session(tenant_id, phone, {'menu': 'main'})

    # ── Daily Summary ──

    async def _show_daily_summary(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        session: Dict[str, Any],
    ) -> None:
        from app.repositories import CaseRepository
        case_repo = CaseRepository()

        stats = await case_repo.get_case_statistics(tenant_id)

        from app.services.tramite_service import tramite_service
        overdue = await tramite_service.get_overdue(tenant_id)
        upcoming = await tramite_service.get_upcoming(tenant_id, days=3)

        total = stats.get('total_cases', 0)
        by_status = stats.get('by_status', {})
        active = total - by_status.get('cerrado', 0) - by_status.get('cancelado', 0)

        msg = (
            f"*Resumen del Dia*\n\n"
            f"Expedientes activos: {active}\n"
            f"Total expedientes: {total}\n"
            f"Tramites vencidos: {len(overdue)}\n"
            f"Tramites proximos (3 dias): {len(upcoming)}\n"
        )

        buttons = [{"id": "alert_overdue", "title": "Ver Vencidos"}]
        if upcoming:
            buttons.append({"id": "alert_upcoming", "title": "Ver Urgentes"})
        buttons.append({"id": "menu_principal", "title": "Menu"})

        await whatsapp_service.send_interactive_buttons(
            to_phone=phone,
            body_text=msg,
            buttons=buttons,
        )

        await self._save_session(tenant_id, phone, {'menu': 'alerts'})

    # ── Search ──

    async def _handle_search(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        search_text = user_input.get('raw', user_input.get('text', '')).strip()
        if not search_text:
            await whatsapp_service.send_text(phone, "Escribe el numero de expediente:")
            return

        from app.repositories import CaseRepository
        case_repo = CaseRepository()

        case = await case_repo.get_by_case_number(tenant_id, search_text)
        if not case:
            await whatsapp_service.send_text(
                phone, f"No se encontro expediente '{search_text}'. Intenta de nuevo o envia 'menu'."
            )
            return

        await self._show_case_detail(tenant_id, phone, staff, case)

    # ── Case Detail ──

    async def _show_case_detail(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        case: Dict[str, Any],
    ) -> None:
        from app.services.case_workflow_service import STATUS_LABELS

        case_id = case['id']
        case_num = case.get('case_number', 'S/N')
        doc_type = case.get('document_type', '')
        status = case.get('status', '')
        status_label = STATUS_LABELS.get(status, status)
        description = case.get('description', '')

        msg = (
            f"*Expediente {case_num}*\n\n"
            f"Tipo: {doc_type}\n"
            f"Estado: {status_label}\n"
        )
        if description:
            msg += f"Descripcion: {description[:100]}\n"

        await whatsapp_service.send_interactive_list(
            to_phone=phone,
            header=f"Exp. {case_num}",
            body_text=msg,
            button_text="Acciones",
            sections=[{
                "title": "Opciones",
                "rows": [
                    {"id": "cd_detail", "title": "Ver Detalle Completo", "description": "Partes, valores, info"},
                    {"id": "cd_transition", "title": "Cambiar Estado", "description": f"Actual: {status_label}"},
                    {"id": "cd_checklist", "title": "Checklist", "description": "Items documentales"},
                    {"id": "cd_tramites", "title": "Tramites", "description": "Semaforo y vencimientos"},
                    {"id": "cd_payments", "title": "Pagos", "description": "Resumen de pagos"},
                    {"id": "cd_notify", "title": "Notificar Cliente", "description": "Enviar update"},
                ],
            }],
            footer="Envia 'menu' para volver al inicio",
        )

        await self._save_session(tenant_id, phone, {
            'menu': 'case_detail',
            'case_id': str(case_id),
            'case_number': case_num,
        })

    async def _handle_case_detail(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')
        case_id = session.get('case_id')

        if not case_id:
            await self._save_session(tenant_id, phone, {'menu': 'main'})
            await self._show_main_menu(phone, staff)
            return

        # Handle case selection from list (case_{uuid})
        if input_id.startswith('case_'):
            case_id = input_id.replace('case_', '')
            from app.repositories import CaseRepository
            case = await CaseRepository().get_by_id(UUID(case_id))
            if case:
                await self._show_case_detail(tenant_id, phone, staff, case)
            else:
                await whatsapp_service.send_text(phone, "Expediente no encontrado.")
            return

        case_uuid = UUID(case_id)

        if input_id == 'cd_detail':
            await self._show_full_detail(tenant_id, phone, case_uuid)
        elif input_id == 'cd_transition':
            await self._show_transitions(tenant_id, phone, staff, case_uuid, session)
        elif input_id == 'cd_checklist':
            await self._show_checklist(tenant_id, phone, staff, case_uuid, session)
        elif input_id == 'cd_tramites':
            await self._show_tramites(tenant_id, phone, staff, case_uuid, session)
        elif input_id == 'cd_payments':
            await self._show_payments(tenant_id, phone, staff, case_uuid, session)
        elif input_id == 'cd_notify':
            await self._notify_client_from_case(tenant_id, phone, case_uuid, session)
        else:
            # Unrecognized input — show case detail again
            from app.repositories import CaseRepository
            case = await CaseRepository().get_by_id(case_uuid)
            if case:
                await self._show_case_detail(tenant_id, phone, staff, case)

    # ── Full Detail ──

    async def _show_full_detail(
        self, tenant_id: UUID, phone: str, case_id: UUID,
    ) -> None:
        from app.repositories import CaseRepository, CasePartyRepository
        from app.services.case_workflow_service import STATUS_LABELS

        case = await CaseRepository().get_case_with_client(case_id)
        if not case:
            await whatsapp_service.send_text(phone, "Expediente no encontrado.")
            return

        parties = await CasePartyRepository().list_by_case(case_id, limit=10)

        case_num = case.get('case_number', 'S/N')
        doc_type = case.get('document_type', '')
        status_label = STATUS_LABELS.get(case.get('status', ''), case.get('status', ''))
        client_info = case.get('client', {})
        client_name = ''
        if client_info:
            client_name = f"{client_info.get('nombre', '')} {client_info.get('apellido_paterno', '')}".strip()

        msg = f"*Expediente {case_num}*\n\n"
        msg += f"Tipo: {doc_type}\n"
        msg += f"Estado: {status_label}\n"
        if client_name:
            msg += f"Cliente: {client_name}\n"

        if case.get('valor_operacion'):
            msg += f"Valor: ${case['valor_operacion']:,.2f}\n"

        if parties:
            msg += "\n*Partes:*\n"
            for p in parties[:5]:
                rol = p.get('rol', '')
                nombre = p.get('nombre_completo', p.get('nombre', ''))
                msg += f"  - {rol}: {nombre}\n"

        await whatsapp_service.send_text(phone, msg)

    # ── Transitions ──

    async def _show_transitions(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        case_id: UUID, session: Dict[str, Any],
    ) -> None:
        from app.repositories import CaseRepository
        from app.services.case_workflow_service import case_workflow_service

        case = await CaseRepository().get_by_id(case_id)
        if not case:
            await whatsapp_service.send_text(phone, "Expediente no encontrado.")
            return

        current = case.get('status', '')
        transitions = case_workflow_service.get_available_transitions(current)

        if not transitions:
            await whatsapp_service.send_text(phone, "No hay transiciones disponibles para el estado actual.")
            return

        # Use buttons for <=3, list for more
        if len(transitions) <= 3:
            buttons = [
                {"id": f"tr_{t['status']}", "title": t['label'][:20]}
                for t in transitions
            ]
            await whatsapp_service.send_interactive_buttons(
                to_phone=phone,
                body_text=f"Cambiar estado de *{session.get('case_number', '')}*\nEstado actual: {case.get('status', '')}",
                buttons=buttons,
                header="Cambiar Estado",
            )
        else:
            rows = [
                {"id": f"tr_{t['status']}", "title": t['label'][:24]}
                for t in transitions[:10]
            ]
            await whatsapp_service.send_interactive_list(
                to_phone=phone,
                body_text=f"Selecciona el nuevo estado para *{session.get('case_number', '')}*:",
                button_text="Ver estados",
                sections=[{"title": "Estados disponibles", "rows": rows}],
            )

        await self._save_session(tenant_id, phone, {
            **session,
            'menu': 'case_transitions',
        })

    async def _handle_case_transitions(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')
        case_id = session.get('case_id')

        if not case_id or not input_id.startswith('tr_'):
            await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail'})
            await whatsapp_service.send_text(phone, "Operacion cancelada.")
            return

        new_status = input_id.replace('tr_', '')
        user_id = UUID(staff['user_id']) if staff.get('user_id') else None

        try:
            from app.services.case_workflow_service import case_workflow_service, STATUS_LABELS
            result = await case_workflow_service.transition(
                case_id=UUID(case_id),
                tenant_id=tenant_id,
                new_status=new_status,
                user_id=user_id,
                notes=f"Cambio via WhatsApp por {staff.get('display_name', '')}",
            )
            new_label = STATUS_LABELS.get(new_status, new_status)
            await whatsapp_service.send_text(
                phone, f"Estado actualizado a: *{new_label}*"
            )
        except ValueError as e:
            await whatsapp_service.send_text(phone, f"Error: {str(e)}")
        except Exception as e:
            logger.error("wa_transition_error", error=str(e))
            await whatsapp_service.send_text(phone, "Error al cambiar estado.")

        # Go back to case detail
        from app.repositories import CaseRepository
        case = await CaseRepository().get_by_id(UUID(case_id))
        if case:
            await self._show_case_detail(tenant_id, phone, staff, case)

    # ── Checklist ──

    async def _show_checklist(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        case_id: UUID, session: Dict[str, Any],
    ) -> None:
        from app.services.checklist_service import checklist_service
        from app.repositories import CaseChecklistRepository

        summary = await checklist_service.get_summary(case_id)
        items = await CaseChecklistRepository().list_by_case(case_id, limit=50)

        total = summary.get('total', 0)
        pct = summary.get('completion_pct', 0)
        by_status = summary.get('by_status', {})

        msg = (
            f"*Checklist — {session.get('case_number', '')}*\n\n"
            f"Progreso: {pct:.0f}%\n"
            f"Total items: {total}\n"
        )
        for status, count in by_status.items():
            msg += f"  {status}: {count}\n"

        # Show pending items that can be marked
        pending = [i for i in items if i.get('status') in ('pendiente', 'solicitado')][:10]

        if pending:
            rows = [
                {
                    "id": f"cl_{i['id']}",
                    "title": (i.get('nombre', 'Item'))[:24],
                    "description": f"Estado: {i.get('status', '')}"[:72],
                }
                for i in pending
            ]
            await whatsapp_service.send_interactive_list(
                to_phone=phone,
                body_text=msg,
                button_text="Marcar recibido",
                sections=[{"title": "Pendientes", "rows": rows}],
                footer="Selecciona para marcar como recibido",
            )
            await self._save_session(tenant_id, phone, {
                **session,
                'menu': 'case_checklist',
            })
        else:
            msg += "\nTodos los items estan completos."
            await whatsapp_service.send_text(phone, msg)
            await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail'})

    async def _handle_case_checklist(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')
        case_id = session.get('case_id')

        if not input_id.startswith('cl_') or not case_id:
            await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail'})
            return

        item_id = input_id.replace('cl_', '')
        user_id = UUID(staff['user_id']) if staff.get('user_id') else None

        try:
            from app.services.checklist_service import checklist_service
            await checklist_service.update_item_status(
                item_id=UUID(item_id),
                status='recibido',
                tenant_id=tenant_id,
                case_id=UUID(case_id),
                user_id=user_id,
                notas=f"Marcado via WhatsApp por {staff.get('display_name', '')}",
            )
            await whatsapp_service.send_text(phone, "Item marcado como recibido.")
        except Exception as e:
            logger.error("wa_checklist_update_error", error=str(e))
            await whatsapp_service.send_text(phone, "Error al actualizar checklist.")

        # Show checklist again
        await self._show_checklist(tenant_id, phone, staff, UUID(case_id), session)

    # ── Tramites ──

    async def _show_tramites(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        case_id: UUID, session: Dict[str, Any],
    ) -> None:
        from app.repositories import CaseTramiteRepository
        from app.services.tramite_service import tramite_service

        tramites = await CaseTramiteRepository().list_by_case(case_id, limit=50)
        enriched = tramite_service.enrich_with_semaforo(tramites)
        semaforo_summary = tramite_service.get_semaforo(enriched)

        msg = (
            f"*Tramites — {session.get('case_number', '')}*\n\n"
            f"Total: {semaforo_summary.get('total', 0)}\n"
            f"🟢 Al dia: {semaforo_summary.get('verde', 0)}\n"
            f"🟡 Pronto: {semaforo_summary.get('amarillo', 0)}\n"
            f"🔴 Vencido: {semaforo_summary.get('rojo', 0)}\n"
            f"⚪ Sin fecha: {semaforo_summary.get('gris', 0)}\n"
        )

        pending = [t for t in enriched if t.get('status') != 'completado'][:10]

        if pending:
            SEMAFORO_ICON = {'verde': '🟢', 'amarillo': '🟡', 'rojo': '🔴', 'gris': '⚪'}
            rows = [
                {
                    "id": f"tm_{t['id']}",
                    "title": f"{SEMAFORO_ICON.get(t.get('semaforo', 'gris'), '⚪')} {t.get('nombre', 'Tramite')}"[:24],
                    "description": f"{t.get('tipo', '')} | {t.get('status', '')}"[:72],
                }
                for t in pending
            ]
            await whatsapp_service.send_interactive_list(
                to_phone=phone,
                body_text=msg,
                button_text="Marcar completado",
                sections=[{"title": "Pendientes", "rows": rows}],
            )
            await self._save_session(tenant_id, phone, {
                **session,
                'menu': 'case_tramites',
            })
        else:
            msg += "\nTodos los tramites completados."
            await whatsapp_service.send_text(phone, msg)
            await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail'})

    async def _handle_case_tramites(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')
        case_id = session.get('case_id')

        if not input_id.startswith('tm_') or not case_id:
            await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail'})
            return

        tramite_id = input_id.replace('tm_', '')
        user_id = UUID(staff['user_id']) if staff.get('user_id') else None

        try:
            from app.services.tramite_service import tramite_service
            await tramite_service.complete(
                tramite_id=UUID(tramite_id),
                tenant_id=tenant_id,
                case_id=UUID(case_id),
                resultado=f"Completado via WhatsApp por {staff.get('display_name', '')}",
                user_id=user_id,
            )
            await whatsapp_service.send_text(phone, "Tramite marcado como completado.")
        except Exception as e:
            logger.error("wa_tramite_complete_error", error=str(e))
            await whatsapp_service.send_text(phone, "Error al completar tramite.")

        await self._show_tramites(tenant_id, phone, staff, UUID(case_id), session)

    # ── Payments ──

    async def _show_payments(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        case_id: UUID, session: Dict[str, Any],
    ) -> None:
        from app.repositories.case_payment_repository import case_payment_repository

        payments = await case_payment_repository.list_by_case(case_id, limit=20)
        totals = await case_payment_repository.get_totals_by_case(case_id)

        msg = f"*Pagos — {session.get('case_number', '')}*\n\n"

        if totals and totals.get('count', 0) > 0:
            for tipo, monto in totals.get('by_tipo', {}).items():
                msg += f"  {tipo}: ${monto:,.2f}\n"
            msg += f"  *Total: ${totals.get('total', 0):,.2f}*\n"
        else:
            msg += "Sin pagos registrados.\n"

        if payments:
            msg += f"\nUltimos {len(payments)} pagos:\n"
            for p in payments[:5]:
                fecha = (p.get('fecha', '') or '')[:10]
                msg += f"  - {p.get('tipo', '')}: ${p.get('monto', 0):,.2f} ({fecha})\n"

        await whatsapp_service.send_text(phone, msg)
        await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail'})

    async def _handle_case_payments(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        # For now, payments view is read-only from WA
        case_id = session.get('case_id')
        if case_id:
            await self._show_payments(tenant_id, phone, staff, UUID(case_id), session)
        else:
            await self._show_main_menu(phone, staff)

    # ── Alerts ──

    async def _show_alerts(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        session: Dict[str, Any],
    ) -> None:
        from app.services.tramite_service import tramite_service

        overdue = await tramite_service.get_overdue(tenant_id)
        upcoming = await tramite_service.get_upcoming(tenant_id, days=5)

        msg = "*Alertas*\n\n"

        if overdue:
            msg += f"🔴 *Vencidos ({len(overdue)}):*\n"
            for t in overdue[:5]:
                case_num = t.get('case_number', t.get('case_id', 'S/N'))
                msg += f"  - {t.get('nombre', '')}: {case_num}\n"
        else:
            msg += "No hay tramites vencidos.\n"

        if upcoming:
            msg += f"\n🟡 *Proximos a vencer ({len(upcoming)}):*\n"
            for t in upcoming[:5]:
                case_num = t.get('case_number', t.get('case_id', 'S/N'))
                fecha = (t.get('fecha_limite', '') or '')[:10]
                msg += f"  - {t.get('nombre', '')}: {case_num} ({fecha})\n"

        buttons = [{"id": "menu_principal", "title": "Menu Principal"}]
        if overdue:
            buttons.insert(0, {"id": "alert_overdue", "title": "Ver Vencidos"})

        await whatsapp_service.send_interactive_buttons(
            to_phone=phone,
            body_text=msg,
            buttons=buttons,
        )

        await self._save_session(tenant_id, phone, {'menu': 'alerts'})

    async def _handle_alerts(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')

        if input_id == 'alert_overdue':
            from app.services.tramite_service import tramite_service
            overdue = await tramite_service.get_overdue(tenant_id)
            if overdue:
                msg = "🔴 *Tramites Vencidos:*\n\n"
                for t in overdue[:10]:
                    case_num = t.get('case_number', t.get('case_id', 'S/N'))
                    fecha = (t.get('fecha_limite', '') or '')[:10]
                    msg += f"- {t.get('nombre', '')}\n  Caso: {case_num} | Venció: {fecha}\n"
                await whatsapp_service.send_text(phone, msg)
            else:
                await whatsapp_service.send_text(phone, "No hay tramites vencidos.")
        elif input_id == 'alert_upcoming':
            from app.services.tramite_service import tramite_service
            upcoming = await tramite_service.get_upcoming(tenant_id, days=7)
            if upcoming:
                msg = "🟡 *Tramites Proximos a Vencer:*\n\n"
                for t in upcoming[:10]:
                    case_num = t.get('case_number', t.get('case_id', 'S/N'))
                    fecha = (t.get('fecha_limite', '') or '')[:10]
                    msg += f"- {t.get('nombre', '')}\n  Caso: {case_num} | Vence: {fecha}\n"
                await whatsapp_service.send_text(phone, msg)
            else:
                await whatsapp_service.send_text(phone, "No hay tramites proximos a vencer.")

        # Always return to main menu after alerts
        await self._save_session(tenant_id, phone, {'menu': 'main'})
        await self._show_main_menu(phone, staff)

    # ── Notify Client ──

    async def _show_notify_select(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        session: Dict[str, Any],
    ) -> None:
        """Show case list for selecting which case's client to notify."""
        from app.repositories import CaseRepository

        active_statuses = [
            'en_revision', 'checklist_pendiente', 'presupuesto',
            'calculo_impuestos', 'en_firma', 'postfirma', 'tramites_gobierno',
            'inscripcion', 'facturacion', 'entrega',
        ]

        all_cases = []
        case_repo = CaseRepository()
        for status in active_statuses:
            cases = await case_repo.list_by_status(tenant_id, status, limit=10)
            all_cases.extend(cases)
            if len(all_cases) >= 10:
                break

        all_cases = all_cases[:10]

        if not all_cases:
            await whatsapp_service.send_text(phone, "No hay expedientes activos para notificar.")
            await self._show_main_menu(phone, staff)
            return

        rows = [
            {
                "id": f"nf_{c['id']}",
                "title": f"{c.get('case_number', 'S/N')}"[:24],
                "description": f"{c.get('document_type', '')} | {c.get('status', '')}"[:72],
            }
            for c in all_cases
        ]

        await whatsapp_service.send_interactive_list(
            to_phone=phone,
            body_text="Selecciona el expediente cuyo cliente deseas notificar:",
            button_text="Seleccionar",
            sections=[{"title": "Expedientes", "rows": rows}],
        )

        await self._save_session(tenant_id, phone, {'menu': 'notify_select'})

    async def _handle_notify_select(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')

        if not input_id.startswith('nf_'):
            await self._save_session(tenant_id, phone, {'menu': 'main'})
            await self._show_main_menu(phone, staff)
            return

        case_id = input_id.replace('nf_', '')
        await self._notify_client_from_case(tenant_id, phone, UUID(case_id), session)

    async def _notify_client_from_case(
        self, tenant_id: UUID, phone: str, case_id: UUID,
        session: Dict[str, Any],
    ) -> None:
        """Send a status update notification to all parties of a case."""
        from app.repositories import CaseRepository, CasePartyRepository
        from app.services.wa_notification_service import wa_notification_service
        from app.services.case_workflow_service import STATUS_LABELS

        case = await CaseRepository().get_by_id(case_id)
        if not case:
            await whatsapp_service.send_text(phone, "Expediente no encontrado.")
            return

        parties = await CasePartyRepository().list_by_case(case_id, limit=20)
        status_label = STATUS_LABELS.get(case.get('status', ''), case.get('status', ''))
        case_num = case.get('case_number', 'S/N')

        notified = 0
        for party in parties:
            party_phone = party.get('telefono')
            if not party_phone:
                continue
            message = (
                f"Actualizacion de su expediente {case_num}:\n"
                f"Estado actual: {status_label}\n"
                f"Notaria ControlNot"
            )
            sent = await wa_notification_service.notify_case_event(
                tenant_id=tenant_id,
                event_type='status_change',
                case_id=case_id,
                phone=party_phone,
                message=message,
            )
            if sent:
                notified += 1

        if notified:
            await whatsapp_service.send_text(
                phone, f"Notificacion enviada a {notified} parte(s) del expediente {case_num}."
            )
        else:
            await whatsapp_service.send_text(
                phone, f"No se pudo notificar: las partes del expediente {case_num} no tienen telefono registrado."
            )

        await self._save_session(tenant_id, phone, {**session, 'menu': 'case_detail', 'case_id': str(case_id)})

    # ── Document Generation Wizard ──

    async def _handle_generate_doc(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        step = session.get('docgen_step', 'select_type')
        input_id = user_input.get('id', '')
        text = user_input.get('text', '')

        if step == 'select_type':
            await self._docgen_select_type(tenant_id, phone, staff, user_input, session)
        elif step == 'select_template':
            await self._docgen_select_template(tenant_id, phone, staff, user_input, session)
        elif step == 'collect_images':
            await self._docgen_collect_images(tenant_id, phone, staff, user_input, session)
        elif step == 'completeness_report':
            await self._docgen_completeness_report(tenant_id, phone, staff, user_input, session)
        elif step == 'review_data':
            await self._docgen_review_data(tenant_id, phone, staff, user_input, session)
        else:
            # Unknown step — restart
            await self._docgen_show_type_list(tenant_id, phone, session)

    async def _docgen_show_type_list(
        self, tenant_id: UUID, phone: str, session: Dict[str, Any],
    ) -> None:
        from app.services.wa_docgen_service import DOC_TYPES

        rows = [
            {"id": f"dtype_{key}", "title": label[:24], "description": f"Tipo: {label}"}
            for key, label in DOC_TYPES.items()
        ]

        await whatsapp_service.send_interactive_list(
            to_phone=phone,
            header="Generar Documento",
            body_text="Selecciona el tipo de documento a generar:",
            button_text="Ver tipos",
            sections=[{"title": "Tipos de documento", "rows": rows}],
            footer="Envia 'menu' para cancelar",
        )

        await self._save_session(tenant_id, phone, {
            'menu': 'generate_doc',
            'docgen_step': 'select_type',
        })

    async def _docgen_select_type(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')

        if not input_id.startswith('dtype_'):
            # First entry — show type list
            await self._docgen_show_type_list(tenant_id, phone, session)
            return

        doc_type = input_id.replace('dtype_', '')
        from app.services.wa_docgen_service import DOC_TYPES
        if doc_type not in DOC_TYPES:
            await whatsapp_service.send_text(phone, "Tipo no valido. Selecciona de la lista.")
            await self._docgen_show_type_list(tenant_id, phone, session)
            return

        # Fetch templates for this type
        from app.services.wa_docgen_service import wa_docgen_service
        templates = await wa_docgen_service.get_templates_for_type(tenant_id, doc_type)

        if not templates:
            await whatsapp_service.send_text(
                phone, f"No hay plantillas disponibles para '{DOC_TYPES[doc_type]}'. Sube una plantilla desde la plataforma web."
            )
            await self._show_main_menu(phone, staff)
            return

        new_session = {
            'menu': 'generate_doc',
            'docgen_step': 'select_template',
            'docgen_type': doc_type,
        }

        if len(templates) == 1:
            # Auto-select the only template
            t = templates[0]
            new_session['docgen_template_id'] = t['id']
            new_session['docgen_template_name'] = t.get('name', 'Plantilla')
            new_session['docgen_images'] = []
            new_session['docgen_prev_image_count'] = 0

            await self._docgen_init_categories(new_session, doc_type)

            await whatsapp_service.send_text(
                phone, f"Plantilla seleccionada: *{t.get('name', 'Plantilla')}*"
            )
            await self._docgen_enter_collect_images(tenant_id, phone, new_session)
            return

        # Multiple templates — show list
        rows = [
            {
                "id": f"tmpl_{t['id']}",
                "title": (t.get('name', 'Plantilla'))[:24],
                "description": (t.get('document_type', ''))[:72],
            }
            for t in templates[:10]
        ]

        await whatsapp_service.send_interactive_list(
            to_phone=phone,
            header="Seleccionar Plantilla",
            body_text=f"Plantillas disponibles para {DOC_TYPES[doc_type]}:",
            button_text="Ver plantillas",
            sections=[{"title": "Plantillas", "rows": rows}],
        )

        await self._save_session(tenant_id, phone, new_session)

    async def _docgen_select_template(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')

        if not input_id.startswith('tmpl_'):
            await whatsapp_service.send_text(phone, "Selecciona una plantilla de la lista.")
            return

        template_id = input_id.replace('tmpl_', '')

        from app.services.wa_docgen_service import wa_docgen_service
        template = await wa_docgen_service.get_template_by_id(template_id)
        if not template:
            await whatsapp_service.send_text(phone, "Plantilla no encontrada. Intenta de nuevo.")
            return

        session['docgen_template_id'] = template_id
        session['docgen_template_name'] = template.get('nombre', 'Plantilla')
        session['docgen_images'] = []
        session['docgen_prev_image_count'] = 0

        doc_type = session.get('docgen_type', '')
        await self._docgen_init_categories(session, doc_type)

        await whatsapp_service.send_text(
            phone, f"Plantilla seleccionada: *{template.get('nombre', 'Plantilla')}*"
        )
        await self._docgen_enter_collect_images(tenant_id, phone, session)

    # ── Category-guided wizard helpers ──

    CATEGORY_ORDER = ["otros", "parte_a", "parte_b"]

    async def _docgen_init_categories(
        self, session: Dict[str, Any], doc_type: str,
    ) -> None:
        """Initialize category session keys if doc_type has CATEGORY_LABELS."""
        from app.services.wa_docgen_service import wa_docgen_service
        cat_labels = wa_docgen_service.get_category_labels(doc_type)

        if cat_labels:
            cats = [c for c in self.CATEGORY_ORDER if c in cat_labels]
            session['docgen_categories'] = cats
            session['docgen_current_cat_index'] = 0
            session['docgen_images_by_cat'] = {c: [] for c in cats}
            session['docgen_cat_warned'] = False
        else:
            # No categories — flat mode
            session.pop('docgen_categories', None)
            session.pop('docgen_current_cat_index', None)
            session.pop('docgen_images_by_cat', None)
            session.pop('docgen_cat_warned', None)

    async def _docgen_send_category_prompt(
        self, phone: str, session: Dict[str, Any],
    ) -> None:
        """Send the category intro message + Siguiente button."""
        from app.services.wa_docgen_service import wa_docgen_service

        cats = session['docgen_categories']
        idx = session['docgen_current_cat_index']
        doc_type = session.get('docgen_type', '')
        cat_labels = wa_docgen_service.get_category_labels(doc_type) or {}

        cat_key = cats[idx]
        label = cat_labels.get(cat_key, cat_key)
        total = len(cats)
        step_num = idx + 1

        # Split label into title and document list
        parts = label.split(' - ', 1)
        title = parts[0]
        docs = parts[1] if len(parts) > 1 else ''

        msg = f"*Paso {step_num} de {total} — {title}*\n"
        if docs:
            msg += f"Envia fotos de: {docs}\n"
        msg += "Cuando termines con estos documentos, presiona *Siguiente*."

        await whatsapp_service.send_text(phone, msg)
        await whatsapp_service.send_interactive_buttons(
            to_phone=phone,
            body_text="Esperando fotos...",
            buttons=[
                {"id": "docgen_next_cat", "title": "Siguiente"},
                {"id": "menu_principal", "title": "Cancelar"},
            ],
        )

    async def _docgen_enter_collect_images(
        self, tenant_id: UUID, phone: str, session: Dict[str, Any],
    ) -> None:
        """Enter collect_images step — send category prompt or flat prompt."""
        session['docgen_step'] = 'collect_images'
        await self._save_session(tenant_id, phone, session)

        if session.get('docgen_categories'):
            await self._docgen_send_category_prompt(phone, session)
        else:
            await whatsapp_service.send_text(
                phone,
                "Envia las fotos de los documentos fuente.\n"
                "Cuando termines, presiona *Listo*."
            )
            await whatsapp_service.send_interactive_buttons(
                to_phone=phone,
                body_text="Esperando fotos...",
                buttons=[
                    {"id": "docgen_done_images", "title": "Listo"},
                    {"id": "menu_principal", "title": "Cancelar"},
                ],
            )

    async def _docgen_finish_collection(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        session: Dict[str, Any],
    ) -> None:
        """All categories done (or flat mode Listo) — extract + validate + report."""
        images = session.get('docgen_images', [])
        if not images:
            await whatsapp_service.send_text(
                phone, "No has enviado fotos. Envia al menos una foto antes de continuar."
            )
            return

        prev_count = session.get('docgen_prev_image_count', 0)
        new_images = images[prev_count:]

        if not new_images:
            await whatsapp_service.send_text(
                phone, "No hay fotos nuevas. Envia mas fotos o escribe 'menu' para cancelar."
            )
            return

        await whatsapp_service.send_text(
            phone, f"Procesando {len(new_images)} foto(s) nueva(s)... esto puede tardar unos segundos."
        )

        try:
            from app.services.wa_docgen_service import wa_docgen_service
            from app.services.anthropic_service import AnthropicExtractionService

            downloaded = await wa_docgen_service.load_stored_images(new_images)
            if not downloaded:
                await whatsapp_service.send_text(
                    phone, "Error: no se pudieron cargar las fotos. Intenta de nuevo."
                )
                return

            doc_type = session.get('docgen_type', 'compraventa')

            new_extracted = await wa_docgen_service.extract_from_images(
                images=downloaded,
                doc_type=doc_type,
                tenant_id=tenant_id,
            )

            existing_extracted = session.get('docgen_extracted', {})
            if existing_extracted:
                extracted = wa_docgen_service.merge_extracted_data(existing_extracted, new_extracted)
            else:
                extracted = new_extracted

            extraction_service = AnthropicExtractionService()
            validation = extraction_service.validate_extracted_data(extracted, doc_type)

            field_sources = wa_docgen_service.get_field_sources(doc_type)

            session['docgen_step'] = 'completeness_report'
            session['docgen_extracted'] = extracted
            session['docgen_validation'] = validation
            session['docgen_prev_image_count'] = len(images)
            await self._save_session(tenant_id, phone, session)

            # Track extraction usage
            await wa_repository.log_command(
                tenant_id=tenant_id,
                staff_phone=phone,
                command='docgen_extraction',
                payload={
                    'doc_type': doc_type,
                    'images_processed': len(new_images),
                    'total_images': len(images),
                },
                result='success',
            )

            report = self._format_completeness_report(
                extracted, validation, field_sources
            )
            await whatsapp_service.send_text(phone, report)

            await whatsapp_service.send_interactive_buttons(
                to_phone=phone,
                body_text="Selecciona una opcion:",
                buttons=[
                    {"id": "docgen_generate_anyway", "title": "Generar asi"},
                    {"id": "docgen_add_more", "title": "Agregar fotos"},
                    {"id": "docgen_cancel", "title": "Cancelar"},
                ],
            )

        except Exception as e:
            logger.error("wa_docgen_extraction_error", error=str(e), traceback=traceback.format_exc())
            await wa_repository.log_command(
                tenant_id=tenant_id,
                staff_phone=phone,
                command='docgen_extraction',
                payload={'doc_type': session.get('docgen_type', 'unknown'), 'images_attempted': len(new_images)},
                result=f'error: {str(e)[:200]}',
            )
            await whatsapp_service.send_text(
                phone, "Error al procesar las fotos. Intenta de nuevo o envia 'menu'."
            )

    async def _send_delayed_photo_summary(
        self, tenant_id: UUID, phone: str, has_categories: bool, delay: float = 4.0,
    ) -> None:
        """Send a single summary message after a batch of photos (debounced)."""
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            return  # Another photo arrived, this summary is superseded

        # Re-read session for accurate counts
        staff = await wa_repository.get_staff_by_phone(tenant_id, phone)
        session = staff.get('session_state', {}) if staff else {}
        images = session.get('docgen_images', [])
        count = len(images)

        if has_categories:
            cats = session.get('docgen_categories', [])
            idx = session.get('docgen_current_cat_index', 0)
            current_cat = cats[idx] if idx < len(cats) else '?'
            cat_images = session.get('docgen_images_by_cat', {}).get(current_cat, [])
            body = f"{count} foto(s) total, {len(cat_images)} en seccion actual. Envia mas o presiona Siguiente."
            buttons = [
                {"id": "docgen_next_cat", "title": "Siguiente"},
                {"id": "menu_principal", "title": "Cancelar"},
            ]
        else:
            body = f"{count} foto(s) recibida(s). Envia mas o presiona Listo."
            buttons = [
                {"id": "docgen_done_images", "title": "Listo"},
                {"id": "menu_principal", "title": "Cancelar"},
            ]

        await whatsapp_service.send_interactive_buttons(to_phone=phone, body_text=body, buttons=buttons)

    # ── Collect images handler ──

    async def _docgen_collect_images(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_type = user_input.get('type', '')
        input_id = user_input.get('id', '')
        has_categories = bool(session.get('docgen_categories'))

        # Received an image — store progressively + evaluate
        if input_type == 'media' and user_input.get('media_id'):
            from app.services.wa_docgen_service import wa_docgen_service

            media_id = user_input['media_id']

            # Acquire per-phone lock to serialize concurrent image webhooks
            async with _get_phone_lock(tenant_id, phone):
                # Re-read session from DB to get latest state (avoid race condition)
                fresh_staff = await wa_repository.get_staff_by_phone(tenant_id, phone)
                if fresh_staff:
                    session = fresh_staff.get('session_state', {}) or {}

                images = session.get('docgen_images', [])
                image_index = len(images)

                store_result = await wa_docgen_service.store_image_progressively(
                    tenant_id=str(tenant_id),
                    phone=phone,
                    media_id=media_id,
                    image_index=image_index,
                )

                if not store_result:
                    await whatsapp_service.send_text(
                        phone, f"Foto {image_index + 1}: Error al descargar. Intenta enviarla de nuevo."
                    )
                    return

                image_record = {
                    'storage_path': store_result['storage_path'],
                    'mime_type': store_result['mime_type'],
                }

                # Save to flat list
                images.append(image_record)
                session['docgen_images'] = images

                # Save to category bucket if applicable
                if has_categories:
                    cats = session['docgen_categories']
                    idx = session.get('docgen_current_cat_index', 0)
                    current_cat = cats[idx]
                    images_by_cat = session.get('docgen_images_by_cat', {})
                    images_by_cat.setdefault(current_cat, []).append(image_record)
                    session['docgen_images_by_cat'] = images_by_cat
                    session['docgen_cat_warned'] = False  # reset warning on new photo

                await self._save_session(tenant_id, phone, session)

            # Quick evaluation (outside lock to not block other photos)
            doc_type = session.get('docgen_type', 'compraventa')
            evaluation = await wa_docgen_service.evaluate_image_quick(
                image_bytes=store_result['content_bytes'],
                mime_type=store_result['mime_type'],
                doc_type=doc_type,
            )

            quality = evaluation.get('quality', '?')
            readable = evaluation.get('readable', 'unknown')
            doc_label = evaluation.get('document_type', 'No evaluado')
            fields = evaluation.get('fields_contributed', [])

            if quality == 'Mala' or readable == 'no':
                feedback = (
                    f"*Foto {image_index + 1}* recibida pero con problemas:\n"
                    f"  Tipo: {doc_label}\n"
                    f"  Calidad: {quality}\n"
                    f"  Legible: {readable}\n"
                    f"  Sugerencia: Toma la foto con mejor iluminacion y enfoque.\n"
                    f"  Puedes enviar otra foto del mismo documento."
                )
            else:
                fields_str = ', '.join(fields[:5]) if fields else '-'
                feedback = (
                    f"*Foto {image_index + 1}* recibida y guardada:\n"
                    f"  Tipo: {doc_label}\n"
                    f"  Calidad: {quality}\n"
                    f"  Legible: {readable}\n"
                    f"  Campos: {fields_str}"
                )

            await whatsapp_service.send_text(phone, feedback)

            # Debounced photo summary — cancel pending and schedule new one
            summary_key = f"{tenant_id}:{phone}"
            if summary_key in _photo_summary_tasks and not _photo_summary_tasks[summary_key].done():
                _photo_summary_tasks[summary_key].cancel()

            _photo_summary_tasks[summary_key] = asyncio.create_task(
                self._send_delayed_photo_summary(tenant_id, phone, has_categories, delay=4.0)
            )
            return

        # "Siguiente" button (category mode) — advance to next category or finish
        if input_id == 'docgen_next_cat' and has_categories:
            from app.services.wa_docgen_service import wa_docgen_service

            cats = session['docgen_categories']
            idx = session.get('docgen_current_cat_index', 0)
            current_cat = cats[idx]
            cat_labels = wa_docgen_service.get_category_labels(session.get('docgen_type', '')) or {}
            cat_images = session.get('docgen_images_by_cat', {}).get(current_cat, [])

            # Warn if no photos in current category (first click)
            if not cat_images and not session.get('docgen_cat_warned'):
                label = cat_labels.get(current_cat, current_cat).split(' - ', 1)[0]
                await whatsapp_service.send_text(
                    phone,
                    f"No enviaste fotos de *{label}*. "
                    f"Los campos de esta seccion quedaran vacios.\n"
                    f"Presiona *Siguiente* otra vez para continuar."
                )
                session['docgen_cat_warned'] = True
                await self._save_session(tenant_id, phone, session)
                await whatsapp_service.send_interactive_buttons(
                    to_phone=phone,
                    body_text="Envia fotos o presiona Siguiente para saltar.",
                    buttons=[
                        {"id": "docgen_next_cat", "title": "Siguiente"},
                        {"id": "menu_principal", "title": "Cancelar"},
                    ],
                )
                return

            # Advance to next category
            next_idx = idx + 1
            if next_idx < len(cats):
                session['docgen_current_cat_index'] = next_idx
                session['docgen_cat_warned'] = False
                await self._save_session(tenant_id, phone, session)
                await self._docgen_send_category_prompt(phone, session)
            else:
                # All categories done — proceed to extraction
                await self._docgen_finish_collection(tenant_id, phone, staff, session)
            return

        # "Listo" button (flat mode) — extract + validate
        if input_id == 'docgen_done_images' and not has_categories:
            await self._docgen_finish_collection(tenant_id, phone, staff, session)
            return

        # Unrecognized input while collecting images
        if has_categories:
            await whatsapp_service.send_text(
                phone, "Envia fotos de los documentos o presiona *Siguiente* cuando termines con esta seccion.\nEscribe *cancelar* o presiona *Cancelar* para salir."
            )
            await whatsapp_service.send_interactive_buttons(
                to_phone=phone,
                body_text="Esperando fotos...",
                buttons=[
                    {"id": "docgen_next_cat", "title": "Siguiente"},
                    {"id": "menu_principal", "title": "Cancelar"},
                ],
            )
        else:
            await whatsapp_service.send_text(
                phone, "Envia fotos de los documentos o presiona *Listo* cuando termines.\nEscribe *cancelar* o presiona *Cancelar* para salir."
            )
            await whatsapp_service.send_interactive_buttons(
                to_phone=phone,
                body_text="Esperando fotos...",
                buttons=[
                    {"id": "docgen_done_images", "title": "Listo"},
                    {"id": "menu_principal", "title": "Cancelar"},
                ],
            )

    async def _docgen_completeness_report(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        """Handle buttons from the completeness report step."""
        input_id = user_input.get('id', '')

        if input_id == 'docgen_cancel':
            await whatsapp_service.send_text(phone, "Generacion cancelada.")
            await self._save_session(tenant_id, phone, {})
            await self._show_main_menu(phone, staff)
            return

        if input_id == 'docgen_add_more':
            # Go back to collect_images, keeping existing data
            # Reset category index to start for category mode
            if session.get('docgen_categories'):
                session['docgen_current_cat_index'] = 0
                session['docgen_cat_warned'] = False
                # Reset per-category image lists (flat list keeps all)
                session['docgen_images_by_cat'] = {
                    c: [] for c in session['docgen_categories']
                }

            await whatsapp_service.send_text(
                phone, "Envia las fotos adicionales de los documentos faltantes."
            )
            await self._docgen_enter_collect_images(tenant_id, phone, session)
            return

        if input_id == 'docgen_generate_anyway':
            # Proceed to generate (same as _docgen_review_data generate flow)
            await whatsapp_service.send_text(phone, "Generando documento...")

            try:
                from app.services.wa_docgen_service import wa_docgen_service

                document = await wa_docgen_service.generate_and_store(
                    tenant_id=tenant_id,
                    template_id=session.get('docgen_template_id', ''),
                    extracted_data=session.get('docgen_extracted', {}),
                    doc_type=session.get('docgen_type', 'compraventa'),
                )

                if not document:
                    await whatsapp_service.send_text(phone, "Error al generar documento. Intenta de nuevo.")
                    await self._save_session(tenant_id, phone, {})
                    await self._show_main_menu(phone, staff)
                    return

                storage_path = document.get('storage_path', '')
                filename = document.get('nombre_documento', 'documento.docx')

                sent = await wa_docgen_service.send_document_via_whatsapp(
                    phone=phone,
                    storage_path=storage_path,
                    filename=filename,
                    caption=f"Documento generado: {filename}",
                )

                if sent:
                    await whatsapp_service.send_text(phone, "Documento generado y enviado exitosamente.")
                else:
                    await whatsapp_service.send_text(
                        phone,
                        "Documento generado pero no se pudo enviar por WhatsApp. "
                        "Puedes descargarlo desde la plataforma web."
                    )

            except Exception as e:
                logger.error("wa_docgen_generate_error", error=str(e))
                await whatsapp_service.send_text(phone, "Error al generar documento. Intenta de nuevo.")

            await self._save_session(tenant_id, phone, {})
            await self._show_main_menu(phone, staff)
            return

        # Unrecognized input — re-show buttons
        await whatsapp_service.send_interactive_buttons(
            to_phone=phone,
            body_text="Selecciona una opcion:",
            buttons=[
                {"id": "docgen_generate_anyway", "title": "Generar asi"},
                {"id": "docgen_add_more", "title": "Agregar fotos"},
                {"id": "docgen_cancel", "title": "Cancelar"},
            ],
        )

    async def _docgen_review_data(
        self, tenant_id: UUID, phone: str, staff: Dict[str, Any],
        user_input: Dict[str, Any], session: Dict[str, Any],
    ) -> None:
        input_id = user_input.get('id', '')

        if input_id == 'docgen_cancel':
            await whatsapp_service.send_text(phone, "Generacion cancelada.")
            await self._save_session(tenant_id, phone, {})
            await self._show_main_menu(phone, staff)
            return

        if input_id == 'docgen_generate':
            await whatsapp_service.send_text(phone, "Generando documento...")

            try:
                from app.services.wa_docgen_service import wa_docgen_service

                document = await wa_docgen_service.generate_and_store(
                    tenant_id=tenant_id,
                    template_id=session.get('docgen_template_id', ''),
                    extracted_data=session.get('docgen_extracted', {}),
                    doc_type=session.get('docgen_type', 'compraventa'),
                )

                if not document:
                    await whatsapp_service.send_text(phone, "Error al generar documento. Intenta de nuevo.")
                    await self._save_session(tenant_id, phone, {})
                    await self._show_main_menu(phone, staff)
                    return

                # Send the document via WhatsApp
                storage_path = document.get('storage_path', '')
                filename = document.get('nombre_documento', 'documento.docx')

                sent = await wa_docgen_service.send_document_via_whatsapp(
                    phone=phone,
                    storage_path=storage_path,
                    filename=filename,
                    caption=f"Documento generado: {filename}",
                )

                if sent:
                    await whatsapp_service.send_text(phone, "Documento generado y enviado exitosamente.")
                else:
                    await whatsapp_service.send_text(
                        phone,
                        "Documento generado pero no se pudo enviar por WhatsApp. "
                        "Puedes descargarlo desde la plataforma web."
                    )

            except Exception as e:
                logger.error("wa_docgen_generate_error", error=str(e))
                await whatsapp_service.send_text(phone, "Error al generar documento. Intenta de nuevo.")

            await self._save_session(tenant_id, phone, {})
            await self._show_main_menu(phone, staff)
            return

        # Unrecognized input — show buttons again
        await whatsapp_service.send_interactive_buttons(
            to_phone=phone,
            body_text="Presiona Generar para crear el documento o Cancelar.",
            buttons=[
                {"id": "docgen_generate", "title": "Generar"},
                {"id": "docgen_cancel", "title": "Cancelar"},
            ],
        )

    @staticmethod
    @staticmethod
    def _format_completeness_report(
        extracted: Dict[str, str],
        validation: Dict,
        field_sources: Dict[str, str],
    ) -> str:
        """Format completeness report as a WhatsApp-friendly message."""
        completeness = validation.get('completeness', 0)
        pct = int(completeness * 100)
        total = validation.get('total_fields', 0)
        found = validation.get('found_fields', 0)
        critical_missing = validation.get('critical_missing', [])
        optional_missing = validation.get('optional_missing', [])

        lines = [f"*Extraccion completa — {pct}%*\n"]

        # Found fields (show up to 10)
        lines.append(f"*Campos encontrados ({found}/{total}):*")
        shown = 0
        for key, value in extracted.items():
            if "NO ENCONTRADO" in str(value):
                continue
            if shown >= 10:
                remaining = found - 10
                if remaining > 0:
                    lines.append(f"  ... y {remaining} campos mas")
                break
            label = key.replace('_', ' ').title()
            val = str(value)[:60]
            lines.append(f"  {label}: {val}")
            shown += 1

        # Critical missing
        if critical_missing:
            lines.append(f"\n*Campos faltantes criticos ({len(critical_missing)}):*")
            for field in critical_missing[:8]:
                source = field_sources.get(field, '')
                source_str = f" ({source})" if source else ''
                label = field.replace('_', ' ').title()
                lines.append(f"  - {label}{source_str}")
            if len(critical_missing) > 8:
                lines.append(f"  ... y {len(critical_missing) - 8} mas")

        # Optional missing
        if optional_missing:
            names = [f.replace('_', ' ').title() for f in optional_missing[:5]]
            suffix = f"... (+{len(optional_missing) - 5})" if len(optional_missing) > 5 else ""
            lines.append(f"\n*Opcionales faltantes ({len(optional_missing)}):*")
            lines.append(f"  {', '.join(names)}{suffix}")

        # Tip: suggest missing document sources
        missing_sources = set()
        for field in critical_missing:
            source = field_sources.get(field, '')
            if source:
                missing_sources.add(source)
        if missing_sources:
            sources_str = ' y '.join(sorted(missing_sources)[:3])
            lines.append(f"\nTip: Envia foto de {sources_str} para completar campos faltantes.")

        return '\n'.join(lines)

    @staticmethod
    def _format_extracted_preview(data: Dict[str, str], max_fields: int = 20) -> str:
        """Format extracted data as a WhatsApp-friendly preview."""
        if not data:
            return "No se extrajeron datos."

        lines = []
        for i, (key, value) in enumerate(data.items()):
            if i >= max_fields:
                lines.append(f"... y {len(data) - max_fields} campos mas")
                break
            label = key.replace('_', ' ').title()
            val = str(value)[:80] if value else '-'
            lines.append(f"*{label}*: {val}")

        return '\n'.join(lines)


# Singleton
menu_handler = WAMenuHandler()
