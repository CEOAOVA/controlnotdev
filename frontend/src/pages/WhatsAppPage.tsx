/**
 * WhatsAppPage
 * Inbox-style chat page with conversation list and chat panel
 */

import { useState, useEffect } from 'react';
import { MessageCircle, RefreshCw } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ConversationList } from '@/components/whatsapp/ConversationList';
import { ChatPanel } from '@/components/whatsapp/ChatPanel';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import type { WAConversation } from '@/api/types/whatsapp-types';

export function WhatsAppPage() {
  const [conversations, setConversations] = useState<WAConversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<WAConversation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadConversations = async () => {
    setIsLoading(true);
    try {
      const data = await whatsappApi.listConversations();
      setConversations(data);
    } catch (err) {
      console.error('Error loading conversations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  return (
    <MainLayout>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-6 h-6 text-green-600" />
            <h1 className="text-2xl font-bold text-neutral-900">WhatsApp</h1>
          </div>
          <Button variant="outline" onClick={loadConversations} disabled={isLoading} className="gap-2">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>

        {/* Chat Layout */}
        <div className="flex gap-4" style={{ height: 'calc(100vh - 220px)' }}>
          {/* Conversation List */}
          <Card className="w-80 flex-shrink-0 overflow-y-auto">
            {isLoading && conversations.length === 0 ? (
              <div className="p-4 space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-neutral-200 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <ConversationList
                conversations={conversations}
                selectedId={selectedConversation?.id}
                onSelect={setSelectedConversation}
              />
            )}
          </Card>

          {/* Chat Panel */}
          <div className="flex-1 min-w-0">
            {selectedConversation ? (
              <ChatPanel conversation={selectedConversation} />
            ) : (
              <Card className="h-full flex items-center justify-center">
                <div className="text-center space-y-2">
                  <MessageCircle className="w-12 h-12 text-neutral-300 mx-auto" />
                  <p className="text-neutral-500">Selecciona una conversacion</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
