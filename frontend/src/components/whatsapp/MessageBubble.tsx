/**
 * MessageBubble
 * Chat message bubble component with media support
 */

import { cn } from '@/lib/utils';
import { Check, CheckCheck, FileText } from 'lucide-react';
import type { WAMessage } from '@/api/types/whatsapp-types';

interface MessageBubbleProps {
  message: WAMessage;
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('es-MX', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isOutgoing = message.sender_type === 'agent' || message.sender_type === 'system';

  const renderContent = () => {
    if (message.message_type === 'image' && message.media_url) {
      return (
        <div className="space-y-1">
          <a href={message.media_url} target="_blank" rel="noopener noreferrer">
            <img
              src={message.media_url}
              alt="Imagen"
              className="max-w-full rounded-md cursor-pointer hover:opacity-90 transition-opacity"
              style={{ maxHeight: 300 }}
            />
          </a>
          {message.content && (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          )}
        </div>
      );
    }

    if (message.message_type === 'document') {
      const filename = message.content || 'Documento';
      return (
        <a
          href={message.media_url || '#'}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 p-2 rounded bg-white/50 hover:bg-white/80 transition-colors"
        >
          <FileText className="w-5 h-5 text-blue-600 shrink-0" />
          <span className="text-sm text-blue-700 underline truncate">{filename}</span>
        </a>
      );
    }

    return (
      <p className="text-sm whitespace-pre-wrap">{message.content || '[Media]'}</p>
    );
  };

  return (
    <div className={cn('flex', isOutgoing ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[70%] rounded-lg px-3 py-2 space-y-1',
          isOutgoing
            ? 'bg-green-100 text-green-900'
            : 'bg-white text-neutral-900 border'
        )}
      >
        {/* Sender label */}
        {!isOutgoing && message.sender_type === 'ai' && (
          <p className="text-xs font-medium text-purple-600">IA</p>
        )}

        {/* Content */}
        {renderContent()}

        {/* Timestamp + Status */}
        <div className={cn('flex items-center gap-1 justify-end')}>
          <span className="text-xs text-neutral-500">{formatTime(message.timestamp)}</span>
          {isOutgoing && (
            message.status === 'read' ? (
              <CheckCheck className="w-3.5 h-3.5 text-blue-500" />
            ) : message.status === 'delivered' ? (
              <CheckCheck className="w-3.5 h-3.5 text-neutral-400" />
            ) : (
              <Check className="w-3.5 h-3.5 text-neutral-400" />
            )
          )}
        </div>
      </div>
    </div>
  );
}
