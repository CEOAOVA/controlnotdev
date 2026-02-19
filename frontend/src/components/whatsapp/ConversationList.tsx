/**
 * ConversationList
 * Sidebar list of WhatsApp conversations
 */

import { cn } from '@/lib/utils';
import { MessageCircle } from 'lucide-react';
import type { WAConversation } from '@/api/types/whatsapp-types';

interface ConversationListProps {
  conversations: WAConversation[];
  selectedId?: string;
  onSelect: (conversation: WAConversation) => void;
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }
  return date.toLocaleDateString('es-MX', { day: '2-digit', month: 'short' });
}

export function ConversationList({ conversations, selectedId, onSelect }: ConversationListProps) {
  if (conversations.length === 0) {
    return (
      <div className="p-4 text-center text-neutral-500 text-sm">
        <MessageCircle className="w-8 h-8 mx-auto mb-2 text-neutral-300" />
        No hay conversaciones
      </div>
    );
  }

  return (
    <div className="divide-y divide-neutral-100">
      {conversations.map((conv) => {
        const contact = conv.wa_contacts;
        const displayName = contact?.name || contact?.phone || 'Desconocido';

        return (
          <div
            key={conv.id}
            className={cn(
              'p-3 cursor-pointer hover:bg-neutral-50 transition-colors',
              selectedId === conv.id && 'bg-primary-50 border-l-2 border-primary-500'
            )}
            onClick={() => onSelect(conv)}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-green-700 font-semibold text-sm">
                {displayName.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-neutral-900 truncate">
                    {displayName}
                  </p>
                  {conv.last_message_at && (
                    <span className="text-xs text-neutral-500">
                      {formatTime(conv.last_message_at)}
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-neutral-500 truncate">
                    {conv.last_message_preview || 'Sin mensajes'}
                  </p>
                  {conv.unread_count > 0 && (
                    <span className="ml-2 bg-green-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {conv.unread_count}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
