/**
 * WhatsAppPage
 * Inbox-style chat page with tabs for conversations, staff, rules, and logs
 */

import { useState, useEffect } from 'react';
import { MessageCircle, RefreshCw, Send } from 'lucide-react';
import { cn } from '@/lib/utils';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ConversationList } from '@/components/whatsapp/ConversationList';
import { ChatPanel } from '@/components/whatsapp/ChatPanel';
import { StaffPhoneManager } from '@/components/whatsapp/StaffPhoneManager';
import { NotificationRulesPanel } from '@/components/whatsapp/NotificationRulesPanel';
import { CommandLogViewer } from '@/components/whatsapp/CommandLogViewer';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import type { WAConversation } from '@/api/types/whatsapp-types';

const STATUS_TABS = [
  { label: 'Todas', value: undefined },
  { label: 'Abiertas', value: 'open' },
  { label: 'Pendientes', value: 'pending' },
  { label: 'Cerradas', value: 'closed' },
] as const;

export function WhatsAppPage() {
  const [conversations, setConversations] = useState<WAConversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<WAConversation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSendingDigest, setIsSendingDigest] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);

  const loadConversations = async (status?: string) => {
    setIsLoading(true);
    try {
      const data = await whatsappApi.listConversations({ status });
      setConversations(data);
    } catch (err) {
      console.error('Error loading conversations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendDigest = async () => {
    setIsSendingDigest(true);
    try {
      await whatsappApi.triggerDailyDigest();
    } catch (err) {
      console.error('Error sending digest:', err);
    } finally {
      setIsSendingDigest(false);
    }
  };

  useEffect(() => {
    loadConversations(statusFilter);

    // Silent poll every 15s
    const interval = setInterval(() => {
      whatsappApi.listConversations({ status: statusFilter })
        .then((data) => {
          setConversations(data);
          // Keep selectedConversation in sync
          if (selectedConversation) {
            const updated = data.find(c => c.id === selectedConversation.id);
            if (updated) setSelectedConversation(updated);
          }
        })
        .catch(() => {});
    }, 15_000);

    return () => clearInterval(interval);
  }, [statusFilter]);

  const handleConversationUpdated = () => {
    loadConversations(statusFilter);
  };

  return (
    <MainLayout>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-6 h-6 text-green-600" />
            <h1 className="text-2xl font-bold text-neutral-900">WhatsApp</h1>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSendDigest}
              disabled={isSendingDigest}
              className="gap-2"
            >
              <Send className={`w-4 h-4 ${isSendingDigest ? 'animate-pulse' : ''}`} />
              Resumen Diario
            </Button>
            <Button variant="outline" onClick={() => loadConversations(statusFilter)} disabled={isLoading} className="gap-2">
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="conversations">
          <TabsList>
            <TabsTrigger value="conversations">Conversaciones</TabsTrigger>
            <TabsTrigger value="staff">Staff</TabsTrigger>
            <TabsTrigger value="rules">Reglas</TabsTrigger>
            <TabsTrigger value="log">Log</TabsTrigger>
          </TabsList>

          <TabsContent value="conversations" className="mt-4">
            {/* Chat Layout */}
            <div className="flex gap-4" style={{ height: 'calc(100vh - 280px)' }}>
              {/* Conversation List */}
              <Card className="w-80 flex-shrink-0 overflow-hidden flex flex-col">
                {/* Status filter tabs */}
                <div className="flex border-b text-xs">
                  {STATUS_TABS.map((opt) => (
                    <button
                      key={opt.label}
                      className={cn(
                        'flex-1 py-2 text-center transition-colors hover:bg-neutral-50',
                        statusFilter === opt.value
                          ? 'bg-green-50 text-green-700 font-medium border-b-2 border-green-500'
                          : 'text-neutral-600'
                      )}
                      onClick={() => setStatusFilter(opt.value)}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>

                <div className="flex-1 overflow-y-auto">
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
                </div>
              </Card>

              {/* Chat Panel */}
              <div className="flex-1 min-w-0">
                {selectedConversation ? (
                  <ChatPanel
                    conversation={selectedConversation}
                    onConversationUpdated={handleConversationUpdated}
                  />
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
          </TabsContent>

          <TabsContent value="staff" className="mt-4">
            <StaffPhoneManager />
          </TabsContent>

          <TabsContent value="rules" className="mt-4">
            <NotificationRulesPanel />
          </TabsContent>

          <TabsContent value="log" className="mt-4">
            <CommandLogViewer />
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
