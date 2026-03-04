-- Migration 013: Add preferences and notifications columns to tenants
-- These JSONB columns store user preferences and notification settings

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS notifications JSONB DEFAULT '{}';

COMMENT ON COLUMN tenants.preferences IS 'User preferences: language, timezone, dateFormat, timeFormat';
COMMENT ON COLUMN tenants.notifications IS 'Notification settings: emailNotifications, documentGenerated, etc.';
