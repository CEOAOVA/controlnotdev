/**
 * PaymentForm
 * Dialog to create/edit a payment
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { X } from 'lucide-react';
import type { PaymentCreateRequest, PaymentTipo, PaymentMetodo } from '@/api/types/payments-types';
import { PAYMENT_TIPO_LABELS, PAYMENT_METODO_LABELS } from '@/api/types/payments-types';

interface PaymentFormProps {
  onSubmit: (data: PaymentCreateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function PaymentForm({ onSubmit, onCancel, isLoading }: PaymentFormProps) {
  const [tipo, setTipo] = useState<PaymentTipo>('honorarios');
  const [concepto, setConcepto] = useState('');
  const [monto, setMonto] = useState('');
  const [metodoPago, setMetodoPago] = useState<PaymentMetodo>('efectivo');
  const [referencia, setReferencia] = useState('');
  const [fechaPago, setFechaPago] = useState('');
  const [recibidoPor, setRecibidoPor] = useState('');
  const [notas, setNotas] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!concepto.trim() || !monto) return;

    const data: PaymentCreateRequest = {
      tipo,
      concepto: concepto.trim(),
      monto: parseFloat(monto),
      metodo_pago: metodoPago,
    };
    if (referencia.trim()) data.referencia = referencia.trim();
    if (fechaPago) data.fecha_pago = new Date(fechaPago).toISOString();
    if (recibidoPor.trim()) data.recibido_por = recibidoPor.trim();
    if (notas.trim()) data.notas = notas.trim();

    await onSubmit(data);
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Registrar Pago</h3>
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <X className="w-4 h-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Tipo */}
          <div className="space-y-2">
            <Label>Tipo de pago *</Label>
            <Select value={tipo} onValueChange={(v) => setTipo(v as PaymentTipo)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(PAYMENT_TIPO_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Metodo */}
          <div className="space-y-2">
            <Label>Metodo de pago</Label>
            <Select value={metodoPago} onValueChange={(v) => setMetodoPago(v as PaymentMetodo)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(PAYMENT_METODO_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Concepto */}
          <div className="space-y-2 md:col-span-2">
            <Label>Concepto *</Label>
            <Input
              value={concepto}
              onChange={(e) => setConcepto(e.target.value)}
              placeholder="Ej: Pago de honorarios notariales"
              required
            />
          </div>

          {/* Monto */}
          <div className="space-y-2">
            <Label>Monto (MXN) *</Label>
            <Input
              type="number"
              step="0.01"
              min="0.01"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              placeholder="0.00"
              required
            />
          </div>

          {/* Referencia */}
          <div className="space-y-2">
            <Label>Referencia</Label>
            <Input
              value={referencia}
              onChange={(e) => setReferencia(e.target.value)}
              placeholder="Num. de referencia o folio"
            />
          </div>

          {/* Fecha */}
          <div className="space-y-2">
            <Label>Fecha de pago</Label>
            <Input
              type="date"
              value={fechaPago}
              onChange={(e) => setFechaPago(e.target.value)}
            />
          </div>

          {/* Recibido por */}
          <div className="space-y-2">
            <Label>Recibido por</Label>
            <Input
              value={recibidoPor}
              onChange={(e) => setRecibidoPor(e.target.value)}
              placeholder="Nombre de quien recibio"
            />
          </div>

          {/* Notas */}
          <div className="space-y-2 md:col-span-2">
            <Label>Notas</Label>
            <Input
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              placeholder="Notas adicionales..."
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading || !concepto.trim() || !monto}>
            {isLoading ? 'Registrando...' : 'Registrar Pago'}
          </Button>
        </div>
      </form>
    </Card>
  );
}
