/**
 * MessageBubble
 * Chat message bubble component
 */

import { cn } from '@/lib/utils';
import { Check, CheckCheck } from 'lucide-react';
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
        <p className="text-sm whitespace-pre-wrap">{message.content || '[Media]'}</p>

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
