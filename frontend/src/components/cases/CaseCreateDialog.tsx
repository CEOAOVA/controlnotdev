import { useState } from 'react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { CaseCreateRequest, CasePriority } from '@/api/types/cases-types';
import type { DocumentType } from '@/types';

interface CaseCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CaseCreateRequest) => Promise<void>;
}

const documentTypes: { value: DocumentType; label: string }[] = [
  { value: 'compraventa', label: 'Compraventa' },
  { value: 'donacion', label: 'Donacion' },
  { value: 'testamento', label: 'Testamento' },
  { value: 'poder', label: 'Poder' },
  { value: 'sociedad', label: 'Sociedad' },
  { value: 'cancelacion', label: 'Cancelacion' },
];

const priorities: { value: CasePriority; label: string }[] = [
  { value: 'baja', label: 'Baja' },
  { value: 'normal', label: 'Normal' },
  { value: 'alta', label: 'Alta' },
  { value: 'urgente', label: 'Urgente' },
];

export function CaseCreateDialog({ open, onOpenChange, onSubmit }: CaseCreateDialogProps) {
  const [caseNumber, setCaseNumber] = useState('');
  const [documentType, setDocumentType] = useState<DocumentType>('compraventa');
  const [clientId, setClientId] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<CasePriority>('normal');
  const [valorOperacion, setValorOperacion] = useState('');
  const [fechaFirma, setFechaFirma] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const resetForm = () => {
    setCaseNumber('');
    setDocumentType('compraventa');
    setClientId('');
    setDescription('');
    setPriority('normal');
    setValorOperacion('');
    setFechaFirma('');
    setError('');
  };

  const handleSubmit = async () => {
    if (!caseNumber.trim()) {
      setError('El numero de expediente es requerido');
      return;
    }
    if (!clientId.trim()) {
      setError('El ID de cliente es requerido');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await onSubmit({
        case_number: caseNumber.trim(),
        document_type: documentType,
        client_id: clientId.trim(),
        description: description.trim() || undefined,
        priority,
        valor_operacion: valorOperacion ? Number(valorOperacion) : undefined,
        fecha_firma: fechaFirma || undefined,
      });
      resetForm();
      onOpenChange(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error al crear expediente');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) resetForm(); onOpenChange(v); }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Nuevo Expediente</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          {error && (
            <div className="p-3 text-sm text-red-700 bg-red-50 rounded-lg">{error}</div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="case-number">Numero de Expediente *</Label>
              <Input
                id="case-number"
                value={caseNumber}
                onChange={(e) => setCaseNumber(e.target.value)}
                placeholder="EXP-001"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="client-id">ID Cliente *</Label>
              <Input
                id="client-id"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="ID del cliente"
                className="mt-1"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Tipo de Documento</Label>
              <Select value={documentType} onValueChange={(v) => setDocumentType(v as DocumentType)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {documentTypes.map((dt) => (
                    <SelectItem key={dt.value} value={dt.value}>{dt.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Prioridad</Label>
              <Select value={priority} onValueChange={(v) => setPriority(v as CasePriority)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {priorities.map((p) => (
                    <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="valor">Valor de Operacion</Label>
              <Input
                id="valor"
                type="number"
                value={valorOperacion}
                onChange={(e) => setValorOperacion(e.target.value)}
                placeholder="0.00"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="fecha-firma">Fecha de Firma</Label>
              <Input
                id="fecha-firma"
                type="date"
                value={fechaFirma}
                onChange={(e) => setFechaFirma(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="description">Descripcion</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Descripcion del expediente..."
              rows={3}
              className="mt-1"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => { resetForm(); onOpenChange(false); }} disabled={submitting}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Creando...' : 'Crear Expediente'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
