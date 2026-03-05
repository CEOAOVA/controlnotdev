/**
 * TemplateSendDialog
 * Modal dialog to browse and send WhatsApp message templates
 */

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import { useToast } from '@/hooks';
import type { WATemplate } from '@/api/types/whatsapp-types';

interface TemplateSendDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  phone?: string;
}

function getTemplateBodyText(template: WATemplate): string {
  const bodyComponent = template.components?.find(
    (c: any) => c.type === 'BODY' || c.type === 'body'
  );
  return bodyComponent?.text || '';
}

export function TemplateSendDialog({ open, onOpenChange, phone: initialPhone }: TemplateSendDialogProps) {
  const toast = useToast();
  const [templates, setTemplates] = useState<WATemplate[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<WATemplate | null>(null);
  const [phone, setPhone] = useState(initialPhone || '');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (open) {
      setIsLoading(true);
      setSelectedTemplate(null);
      setPhone(initialPhone || '');
      whatsappApi.listTemplates()
        .then((all) => {
          const approved = all.filter(t => t.is_active && t.status === 'APPROVED');
          setTemplates(approved);
        })
        .catch(() => {
          toast.error('Error al cargar plantillas');
        })
        .finally(() => setIsLoading(false));
    }
  }, [open]);

  const handleSend = async () => {
    if (!selectedTemplate || !phone.trim()) return;
    setIsSending(true);
    try {
      await whatsappApi.sendTemplate(phone.trim(), selectedTemplate.name, selectedTemplate.language);
      toast.success('Plantilla enviada');
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al enviar plantilla');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Enviar Plantilla</DialogTitle>
        </DialogHeader>

        {/* Phone input */}
        <div>
          <label className="text-sm font-medium text-neutral-700 mb-1 block">Telefono</label>
          <Input
            placeholder="521234567890"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        {/* Template list */}
        <div>
          <label className="text-sm font-medium text-neutral-700 mb-1 block">Plantilla</label>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-12 bg-neutral-100 rounded animate-pulse" />
              ))}
            </div>
          ) : templates.length === 0 ? (
            <p className="text-sm text-neutral-500 py-4 text-center">No hay plantillas aprobadas</p>
          ) : (
            <div className="max-h-48 overflow-y-auto border rounded-md divide-y">
              {templates.map((tpl) => (
                <div
                  key={tpl.id}
                  className={cn(
                    'p-3 cursor-pointer transition-colors hover:bg-neutral-50',
                    selectedTemplate?.id === tpl.id && 'bg-green-50 border-l-2 border-green-500'
                  )}
                  onClick={() => setSelectedTemplate(tpl)}
                >
                  <p className="text-sm font-medium">{tpl.display_name || tpl.name}</p>
                  <p className="text-xs text-neutral-500">{tpl.category} &middot; {tpl.language}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Preview */}
        {selectedTemplate && (
          <div>
            <label className="text-sm font-medium text-neutral-700 mb-1 block">Vista previa</label>
            <div className="p-3 bg-neutral-50 rounded-md border text-sm text-neutral-700 whitespace-pre-wrap">
              {getTemplateBodyText(selectedTemplate) || 'Sin contenido de texto'}
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            onClick={handleSend}
            disabled={!selectedTemplate || !phone.trim() || isSending}
          >
            {isSending ? 'Enviando...' : 'Enviar Plantilla'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
