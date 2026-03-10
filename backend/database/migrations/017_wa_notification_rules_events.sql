-- =============================================
-- Migration 017: Expand wa_notification_rules event_type CHECK constraint
-- =============================================
-- Adds new event types needed by P0 features:
--   - checklist_updated: when a single checklist item is marked as received
--   - auto_reply: flag to enable/disable AI auto-reply per tenant
--   - daily_digest: daily summary notifications to staff
-- Existing types preserved: case_created, status_change, tramite_vencido,
--   checklist_complete, payment_received

ALTER TABLE wa_notification_rules
  DROP CONSTRAINT IF EXISTS wa_notification_rules_event_check;

ALTER TABLE wa_notification_rules
  ADD CONSTRAINT wa_notification_rules_event_check
  CHECK (event_type IN (
    'case_created',
    'status_change',
    'tramite_vencido',
    'checklist_complete',
    'checklist_updated',
    'payment_received',
    'auto_reply',
    'daily_digest'
  ));
