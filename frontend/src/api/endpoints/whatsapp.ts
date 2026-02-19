/**
 * WhatsApp API Endpoints
 * Conversations, messages, templates
 */

import { apiClient } from '../client';
import type { WAConversation, WAMessage, WATemplate } from '../types/whatsapp-types';

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
};
