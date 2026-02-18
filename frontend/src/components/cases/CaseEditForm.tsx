import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import type { CaseDetail, CaseUpdateRequest, CasePriority } from '@/api/types/cases-types';

interface CaseEditFormProps {
  caseData: CaseDetail;
  onSave: (data: CaseUpdateRequest) => Promise<void>;
}

const priorities: { value: CasePriority; label: string }[] = [
  { value: 'baja', label: 'Baja' },
  { value: 'normal', label: 'Normal' },
  { value: 'alta', label: 'Alta' },
  { value: 'urgente', label: 'Urgente' },
];

export function CaseEditForm({ caseData, onSave }: CaseEditFormProps) {
  const [description, setDescription] = useState(caseData.description || '');
  const [priority, setPriority] = useState<CasePriority>(caseData.priority || 'normal');
  const [escrituraNumber, setEscrituraNumber] = useState(caseData.escritura_number || '');
  const [volumen, setVolumen] = useState(caseData.volumen || '');
  const [folioReal, setFolioReal] = useState(caseData.folio_real || '');
  const [valorOperacion, setValorOperacion] = useState(
    caseData.valor_operacion?.toString() || ''
  );
  const [fechaFirma, setFechaFirma] = useState(caseData.fecha_firma || '');
  const [notas, setNotas] = useState(caseData.notas || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({
        description: description || undefined,
        priority,
        escritura_number: escrituraNumber || undefined,
        volumen: volumen || undefined,
        folio_real: folioReal || undefined,
        valor_operacion: valorOperacion ? Number(valorOperacion) : undefined,
        fecha_firma: fechaFirma || undefined,
        notas: notas || undefined,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="p-6 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label>Numero de Expediente</Label>
          <Input value={caseData.case_number} disabled className="mt-1 bg-neutral-50" />
        </div>
        <div>
          <Label>Tipo de Documento</Label>
          <Input value={caseData.document_type} disabled className="mt-1 bg-neutral-50 capitalize" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label>Prioridad</Label>
          <Select value={priority} onValueChange={(v) => setPriority(v as CasePriority)}>
            <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
            <SelectContent>
              {priorities.map((p) => (
                <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="escritura">Numero de Escritura</Label>
          <Input id="escritura" value={escrituraNumber} onChange={(e) => setEscrituraNumber(e.target.value)} className="mt-1" />
        </div>
        <div>
          <Label htmlFor="volumen">Volumen</Label>
          <Input id="volumen" value={volumen} onChange={(e) => setVolumen(e.target.value)} className="mt-1" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label htmlFor="folio">Folio Real</Label>
          <Input id="folio" value={folioReal} onChange={(e) => setFolioReal(e.target.value)} className="mt-1" />
        </div>
        <div>
          <Label htmlFor="valor">Valor de Operacion</Label>
          <Input id="valor" type="number" value={valorOperacion} onChange={(e) => setValorOperacion(e.target.value)} className="mt-1" />
        </div>
        <div>
          <Label htmlFor="fecha">Fecha de Firma</Label>
          <Input id="fecha" type="date" value={fechaFirma} onChange={(e) => setFechaFirma(e.target.value)} className="mt-1" />
        </div>
      </div>

      <div>
        <Label htmlFor="desc">Descripcion</Label>
        <Textarea id="desc" value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="mt-1" />
      </div>

      <div>
        <Label htmlFor="notas">Notas</Label>
        <Textarea id="notas" value={notas} onChange={(e) => setNotas(e.target.value)} rows={3} className="mt-1" />
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Guardando...' : 'Guardar Cambios'}
        </Button>
      </div>
    </Card>
  );
}
