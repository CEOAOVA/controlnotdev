/**
 * WhatsApp API Endpoints
 * Conversations, messages, templates, documents
 */

import { apiClient } from '../client';
import type {
  WAConversation,
  WAMessage,
  WATemplate,
  WAStaffPhone,
  WANotificationRule,
  WACommandLog,
} from '../types/whatsapp-types';

export const whatsappApi = {
  listConversations: async (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<WAConversation[]> => {
    const response = await apiClient.get('/whatsapp/conversations', { params });
    return response.data.conversations;
  },

  getMessages: async (conversationId: string, limit = 50, offset = 0): Promise<WAMessage[]> => {
    const response = await apiClient.get(`/whatsapp/conversations/${conversationId}/messages`, {
      params: { limit, offset },
    });
    return response.data.messages;
  },

  sendMessage: async (conversationId: string, content: string): Promise<WAMessage> => {
    const response = await apiClient.post('/whatsapp/send', {
      conversation_id: conversationId,
      content,
      message_type: 'text',
    });
    return response.data.data;
  },

  sendDocument: async (
    conversationId: string,
    documentUrl: string,
    filename: string,
    caption?: string,
  ): Promise<WAMessage> => {
    const response = await apiClient.post('/whatsapp/send-document', {
      conversation_id: conversationId,
      document_url: documentUrl,
      filename,
      caption,
    });
    return response.data.data;
  },

  sendTemplate: async (phone: string, templateName: string, language = 'es'): Promise<any> => {
    const response = await apiClient.post('/whatsapp/send-template', {
      phone,
      template_name: templateName,
      language,
    });
    return response.data;
  },

  listTemplates: async (): Promise<WATemplate[]> => {
    const response = await apiClient.get('/whatsapp/templates');
    return response.data.templates;
  },

  linkContact: async (contactId: string, clientId: string): Promise<any> => {
    const response = await apiClient.post('/whatsapp/contacts/link', {
      contact_id: contactId,
      client_id: clientId,
    });
    return response.data;
  },

  assignConversation: async (conversationId: string, agentId?: string): Promise<any> => {
    const response = await apiClient.put(`/whatsapp/conversations/${conversationId}/assign`, null, {
      params: { agent_id: agentId },
    });
    return response.data;
  },

  closeConversation: async (conversationId: string): Promise<any> => {
    const response = await apiClient.put(`/whatsapp/conversations/${conversationId}/close`);
    return response.data;
  },

  markAsRead: async (conversationId: string): Promise<any> => {
    const response = await apiClient.put(`/whatsapp/conversations/${conversationId}/read`);
    return response.data;
  },

  getSuggestedReply: async (conversationId: string): Promise<{ suggestion: string | null }> => {
    const response = await apiClient.get(`/whatsapp/conversations/${conversationId}/suggest`);
    return response.data;
  },

  // Staff Phones
  listStaffPhones: async (): Promise<WAStaffPhone[]> => {
    const response = await apiClient.get('/whatsapp/staff-phones');
    return response.data.staff_phones;
  },

  createStaffPhone: async (data: {
    phone: string;
    display_name: string;
    user_id?: string;
    role?: string;
  }): Promise<WAStaffPhone> => {
    const response = await apiClient.post('/whatsapp/staff-phones', data);
    return response.data.staff_phone;
  },

  updateStaffPhone: async (id: string, data: Partial<WAStaffPhone>): Promise<WAStaffPhone> => {
    const response = await apiClient.put(`/whatsapp/staff-phones/${id}`, data);
    return response.data.staff_phone;
  },

  deleteStaffPhone: async (id: string): Promise<void> => {
    await apiClient.delete(`/whatsapp/staff-phones/${id}`);
  },

  // Notification Rules
  listNotificationRules: async (): Promise<WANotificationRule[]> => {
    const response = await apiClient.get('/whatsapp/notification-rules');
    return response.data.notification_rules;
  },

  createNotificationRule: async (data: {
    event_type: string;
    is_active?: boolean;
    notify_staff?: boolean;
    template_id?: string;
    message_text?: string;
  }): Promise<WANotificationRule> => {
    const response = await apiClient.post('/whatsapp/notification-rules', data);
    return response.data.notification_rule;
  },

  updateNotificationRule: async (id: string, data: Partial<WANotificationRule>): Promise<WANotificationRule> => {
    const response = await apiClient.put(`/whatsapp/notification-rules/${id}`, data);
    return response.data.notification_rule;
  },

  deleteNotificationRule: async (id: string): Promise<void> => {
    await apiClient.delete(`/whatsapp/notification-rules/${id}`);
  },

  // Command Log
  listCommandLog: async (params?: {
    staff_phone?: string;
    limit?: number;
    offset?: number;
  }): Promise<WACommandLog[]> => {
    const response = await apiClient.get('/whatsapp/command-log', { params });
    return response.data.command_log;
  },

  // Daily Digest
  triggerDailyDigest: async (): Promise<any> => {
    const response = await apiClient.post('/whatsapp/daily-digest');
    return response.data;
  },
};
