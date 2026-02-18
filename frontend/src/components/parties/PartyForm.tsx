import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { PartyCreateRequest, CaseParty } from '@/api/types/cases-types';

interface PartyFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: PartyCreateRequest) => Promise<void>;
  initialData?: CaseParty;
}

const roles = ['vendedor', 'comprador', 'donante', 'donatario', 'testador', 'poderdante', 'apoderado', 'representante', 'otro'];

export function PartyForm({ open, onOpenChange, onSubmit, initialData }: PartyFormProps) {
  const [role, setRole] = useState('vendedor');
  const [nombre, setNombre] = useState('');
  const [rfc, setRfc] = useState('');
  const [tipoPersona, setTipoPersona] = useState<'fisica' | 'moral'>('fisica');
  const [email, setEmail] = useState('');
  const [telefono, setTelefono] = useState('');
  const [representanteLegal, setRepresentanteLegal] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setRole(initialData.role);
      setNombre(initialData.nombre);
      setRfc(initialData.rfc || '');
      setTipoPersona(initialData.tipo_persona || 'fisica');
      setEmail(initialData.email || '');
      setTelefono(initialData.telefono || '');
      setRepresentanteLegal(initialData.representante_legal || '');
    } else {
      setRole('vendedor');
      setNombre('');
      setRfc('');
      setTipoPersona('fisica');
      setEmail('');
      setTelefono('');
      setRepresentanteLegal('');
    }
  }, [initialData, open]);

  const handleSubmit = async () => {
    if (!nombre.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit({
        role,
        nombre: nombre.trim(),
        rfc: rfc.trim() || undefined,
        tipo_persona: tipoPersona,
        email: email.trim() || undefined,
        telefono: telefono.trim() || undefined,
        representante_legal: representanteLegal.trim() || undefined,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{initialData ? 'Editar Parte' : 'Agregar Parte'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Rol</Label>
              <Select value={role} onValueChange={setRole}>
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {roles.map((r) => (
                    <SelectItem key={r} value={r} className="capitalize">{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Tipo Persona</Label>
              <Select value={tipoPersona} onValueChange={(v) => setTipoPersona(v as 'fisica' | 'moral')}>
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="fisica">Fisica</SelectItem>
                  <SelectItem value="moral">Moral</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="nombre">Nombre Completo *</Label>
            <Input id="nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Nombre completo" className="mt-1" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="rfc">RFC</Label>
              <Input id="rfc" value={rfc} onChange={(e) => setRfc(e.target.value)} placeholder="RFC" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email@ejemplo.com" className="mt-1" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="tel">Telefono</Label>
              <Input id="tel" value={telefono} onChange={(e) => setTelefono(e.target.value)} placeholder="Telefono" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="rep">Representante Legal</Label>
              <Input id="rep" value={representanteLegal} onChange={(e) => setRepresentanteLegal(e.target.value)} placeholder="Si aplica" className="mt-1" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>Cancelar</Button>
          <Button onClick={handleSubmit} disabled={!nombre.trim() || submitting}>
            {submitting ? 'Guardando...' : initialData ? 'Actualizar' : 'Agregar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
