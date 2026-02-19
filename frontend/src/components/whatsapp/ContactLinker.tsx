/**
 * ContactLinker
 * Component to link a WhatsApp contact with a client
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Link2 } from 'lucide-react';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import { useToast } from '@/hooks';

interface ContactLinkerProps {
  contactId: string;
  contactName?: string;
  onLinked?: () => void;
}

export function ContactLinker({ contactId, contactName, onLinked }: ContactLinkerProps) {
  const toast = useToast();
  const [clientId, setClientId] = useState('');
  const [isLinking, setIsLinking] = useState(false);

  const handleLink = async () => {
    if (!clientId.trim()) return;
    setIsLinking(true);
    try {
      await whatsappApi.linkContact(contactId, clientId.trim());
      toast.success('Contacto vinculado con cliente');
      onLinked?.();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al vincular');
    } finally {
      setIsLinking(false);
    }
  };

  return (
    <Card className="p-4">
      <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
        <Link2 className="w-4 h-4" />
        Vincular {contactName || 'contacto'} con cliente
      </h4>
      <div className="flex gap-2">
        <div className="flex-1">
          <Label className="sr-only">Client ID</Label>
          <Input
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            placeholder="UUID del cliente"
          />
        </div>
        <Button onClick={handleLink} disabled={isLinking || !clientId.trim()}>
          {isLinking ? 'Vinculando...' : 'Vincular'}
        </Button>
      </div>
    </Card>
  );
}
