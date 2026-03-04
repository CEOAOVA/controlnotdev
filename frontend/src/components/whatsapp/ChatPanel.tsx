/**
 * ChatPanel
 * Main chat panel showing messages for a conversation with AI suggestions
 */

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import { useToast } from '@/hooks';
import type { WAConversation, WAMessage } from '@/api/types/whatsapp-types';

interface ChatPanelProps {
  conversation: WAConversation;
}

export function ChatPanel({ conversation }: ChatPanelProps) {
  const toast = useToast();
  const [messages, setMessages] = useState<WAMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadMessages = async () => {
    setIsLoading(true);
    try {
      const msgs = await whatsappApi.getMessages(conversation.id);
      setMessages(msgs);
    } catch (err) {
      console.error('Error loading messages:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSuggestion = async () => {
    try {
      const result = await whatsappApi.getSuggestedReply(conversation.id);
      setSuggestion(result.suggestion || null);
    } catch {
      setSuggestion(null);
    }
  };

  useEffect(() => {
    loadMessages();
    setSuggestion(null);
  }, [conversation.id]);

  // Load suggestion after messages are loaded
  useEffect(() => {
    if (!isLoading && messages.length > 0) {
      loadSuggestion();
    }
  }, [isLoading, messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (content: string) => {
    try {
      const sent = await whatsappApi.sendMessage(conversation.id, content);
      if (sent) {
        setMessages((prev) => [...prev, sent]);
        setSuggestion(null);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al enviar mensaje');
    }
  };

  const handleUseSuggestion = () => {
    if (suggestion) {
      handleSend(suggestion);
    }
  };

  const contact = conversation.wa_contacts;
  const displayName = contact?.name || contact?.phone || 'Conversacion';

  return (
    <Card className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 p-3 border-b">
        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-green-700 font-semibold">
          {displayName.charAt(0).toUpperCase()}
        </div>
        <div>
          <p className="font-medium text-neutral-900">{displayName}</p>
          {contact?.phone && (
            <p className="text-xs text-neutral-500">{contact.phone}</p>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-neutral-50 min-h-0">
        {isLoading ? (
          <div className="space-y-3">
            <div className="h-10 bg-neutral-200 rounded-lg animate-pulse w-1/2" />
            <div className="h-10 bg-neutral-200 rounded-lg animate-pulse w-2/3 ml-auto" />
            <div className="h-10 bg-neutral-200 rounded-lg animate-pulse w-1/2" />
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-neutral-500 text-sm py-8">
            No hay mensajes en esta conversacion
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* AI Suggestion Chip */}
      {suggestion && (
        <div className="flex items-center gap-2 px-3 py-2 bg-purple-50 border-t border-purple-100">
          <span className="text-xs font-medium text-purple-700 shrink-0">IA sugiere:</span>
          <span className="text-sm text-purple-900 truncate flex-1">{suggestion}</span>
          <Button
            size="sm"
            variant="outline"
            className="text-purple-700 border-purple-300 hover:bg-purple-100 shrink-0"
            onClick={handleUseSuggestion}
          >
            Usar
          </Button>
        </div>
      )}

      {/* Input */}
      <MessageInput onSend={handleSend} />
    </Card>
  );
}
