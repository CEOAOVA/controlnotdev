/**
 * MessageInput
 * Input for sending WhatsApp messages with file attachment support
 */

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Paperclip, LayoutTemplate } from 'lucide-react';

interface MessageInputProps {
  onSend: (content: string) => Promise<void>;
  onAttachFile?: (file: File) => Promise<void>;
  onTemplateClick?: () => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, onAttachFile, onTemplateClick, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!message.trim() || sending) return;
    setSending(true);
    try {
      await onSend(message.trim());
      setMessage('');
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !onAttachFile) return;
    setSending(true);
    try {
      await onAttachFile(file);
    } finally {
      setSending(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex items-center gap-2 p-3 border-t bg-white">
      {onAttachFile && (
        <>
          <Button
            size="icon"
            variant="ghost"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || sending}
            title="Adjuntar archivo"
          >
            <Paperclip className="w-4 h-4" />
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/*,.pdf,.doc,.docx"
            onChange={handleFileChange}
          />
        </>
      )}
      {onTemplateClick && (
        <Button
          size="icon"
          variant="ghost"
          onClick={onTemplateClick}
          disabled={disabled || sending}
          title="Enviar plantilla"
        >
          <LayoutTemplate className="w-4 h-4" />
        </Button>
      )}
      <Input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Escribe un mensaje..."
        disabled={disabled || sending}
        className="flex-1"
      />
      <Button
        size="icon"
        onClick={handleSend}
        disabled={disabled || sending || !message.trim()}
      >
        <Send className="w-4 h-4" />
      </Button>
    </div>
  );
}
