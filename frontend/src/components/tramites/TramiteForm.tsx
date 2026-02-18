import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { TramiteCreateRequest, Tramite } from '@/api/types/cases-types';

interface TramiteFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TramiteCreateRequest) => Promise<void>;
  initialData?: Tramite;
}

export function TramiteForm({ open, onOpenChange, onSubmit, initialData }: TramiteFormProps) {
  const [tipo, setTipo] = useState('');
  const [nombre, setNombre] = useState('');
  const [fechaLimite, setFechaLimite] = useState('');
  const [costo, setCosto] = useState('');
  const [notas, setNotas] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setTipo(initialData.tipo);
      setNombre(initialData.nombre);
      setFechaLimite(initialData.fecha_limite || '');
      setCosto(initialData.costo?.toString() || '');
      setNotas(initialData.notas || '');
    } else {
      setTipo('');
      setNombre('');
      setFechaLimite('');
      setCosto('');
      setNotas('');
    }
  }, [initialData, open]);

  const handleSubmit = async () => {
    if (!nombre.trim() || !tipo.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit({
        tipo: tipo.trim(),
        nombre: nombre.trim(),
        fecha_limite: fechaLimite || undefined,
        costo: costo ? Number(costo) : undefined,
        notas: notas.trim() || undefined,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{initialData ? 'Editar Tramite' : 'Nuevo Tramite'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="tipo">Tipo *</Label>
              <Input id="tipo" value={tipo} onChange={(e) => setTipo(e.target.value)} placeholder="pago_impuestos, registro, etc." className="mt-1" />
            </div>
            <div>
              <Label htmlFor="nombre-t">Nombre *</Label>
              <Input id="nombre-t" value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Pago ISR, Registro RPP..." className="mt-1" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="fecha-lim">Fecha Limite</Label>
              <Input id="fecha-lim" type="date" value={fechaLimite} onChange={(e) => setFechaLimite(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="costo">Costo</Label>
              <Input id="costo" type="number" value={costo} onChange={(e) => setCosto(e.target.value)} placeholder="0.00" className="mt-1" />
            </div>
          </div>
          <div>
            <Label htmlFor="notas-t">Notas</Label>
            <Textarea id="notas-t" value={notas} onChange={(e) => setNotas(e.target.value)} rows={2} className="mt-1" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>Cancelar</Button>
          <Button onClick={handleSubmit} disabled={!nombre.trim() || !tipo.trim() || submitting}>
            {submitting ? 'Guardando...' : initialData ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
