/**
 * WhatsApp Types
 * Types for WhatsApp messaging integration
 */

export type ConversationStatus = 'open' | 'closed' | 'pending';
export type SenderType = 'client' | 'agent' | 'system' | 'ai';
export type MessageType = 'text' | 'image' | 'document' | 'audio' | 'template';
export type MessageStatus = 'sent' | 'delivered' | 'read' | 'failed';

export interface WAContact {
  id: string;
  phone: string;
  name?: string;
  client_id?: string;
}

export interface WAConversation {
  id: string;
  tenant_id: string;
  contact_id: string;
  case_id?: string;
  assigned_to?: string;
  status: ConversationStatus;
  last_message_at?: string;
  last_message_preview?: string;
  unread_count: number;
  ai_enabled: boolean;
  wa_contacts?: WAContact;
  created_at: string;
  updated_at: string;
}

export interface WAMessage {
  id: string;
  tenant_id: string;
  conversation_id: string;
  whatsapp_message_id?: string;
  sender_type: SenderType;
  sender_id?: string;
  content?: string;
  message_type: MessageType;
  media_url?: string;
  media_path?: string;
  status: MessageStatus;
  reply_to_id?: string;
  metadata?: Record<string, any>;
  timestamp: string;
  created_at: string;
}

export interface WATemplate {
  id: string;
  tenant_id: string;
  name: string;
  display_name?: string;
  category: string;
  language: string;
  status: string;
  components: any[];
  is_active: boolean;
  created_at: string;
}
