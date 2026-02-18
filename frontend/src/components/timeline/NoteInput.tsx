import { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface NoteInputProps {
  onSubmit: (note: string) => Promise<void>;
}

export function NoteInput({ onSubmit }: NoteInputProps) {
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!note.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit(note.trim());
      setNote('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Textarea
        placeholder="Agregar una nota..."
        value={note}
        onChange={(e) => setNote(e.target.value)}
        rows={2}
        className="flex-1"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            handleSubmit();
          }
        }}
      />
      <Button
        onClick={handleSubmit}
        disabled={!note.trim() || submitting}
        size="icon"
        className="self-end"
      >
        <Send className="w-4 h-4" />
      </Button>
    </div>
  );
}
