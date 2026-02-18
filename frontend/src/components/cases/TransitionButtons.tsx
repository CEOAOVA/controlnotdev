import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { Transition } from '@/api/types/cases-types';

interface TransitionButtonsProps {
  transitions: Transition[];
  onTransition: (status: string, notes?: string) => Promise<void>;
  isLoading?: boolean;
}

export function TransitionButtons({ transitions, onTransition, isLoading }: TransitionButtonsProps) {
  const [confirmDialog, setConfirmDialog] = useState<Transition | null>(null);
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const needsConfirmation = (status: string) =>
    status === 'cancelado' || status === 'suspendido';

  const getButtonVariant = (status: string) => {
    if (status === 'cancelado') return 'destructive' as const;
    if (status === 'suspendido') return 'outline' as const;
    return 'default' as const;
  };

  const handleClick = async (transition: Transition) => {
    if (needsConfirmation(transition.status)) {
      setConfirmDialog(transition);
      setReason('');
      return;
    }

    setSubmitting(true);
    try {
      await onTransition(transition.status);
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirm = async () => {
    if (!confirmDialog || !reason.trim()) return;

    setSubmitting(true);
    try {
      await onTransition(confirmDialog.status, reason);
      setConfirmDialog(null);
      setReason('');
    } finally {
      setSubmitting(false);
    }
  };

  if (transitions.length === 0) return null;

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {transitions.map((t) => (
          <Button
            key={t.status}
            variant={getButtonVariant(t.status)}
            size="sm"
            onClick={() => handleClick(t)}
            disabled={isLoading || submitting}
          >
            {t.label}
          </Button>
        ))}
      </div>

      <Dialog open={!!confirmDialog} onOpenChange={() => setConfirmDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {confirmDialog?.status === 'cancelado' ? 'Cancelar Expediente' : 'Suspender Expediente'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <p className="text-sm text-neutral-600">
              {confirmDialog?.status === 'cancelado'
                ? 'Esta accion es permanente. Indique el motivo de la cancelacion.'
                : 'Indique el motivo de la suspension. El expediente podra ser reanudado despues.'}
            </p>
            <Textarea
              placeholder="Motivo..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDialog(null)} disabled={submitting}>
              Cancelar
            </Button>
            <Button
              variant={confirmDialog?.status === 'cancelado' ? 'destructive' : 'default'}
              onClick={handleConfirm}
              disabled={!reason.trim() || submitting}
            >
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
