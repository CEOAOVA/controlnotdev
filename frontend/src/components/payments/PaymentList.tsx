/**
 * PaymentList
 * Shows list of payments with totals for a case
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Plus, Trash2, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PaymentForm } from './PaymentForm';
import type {
  CasePayment,
  PaymentTotals,
  PaymentCreateRequest,
} from '@/api/types/payments-types';
import { PAYMENT_TIPO_LABELS, PAYMENT_METODO_LABELS } from '@/api/types/payments-types';

interface PaymentListProps {
  payments: CasePayment[];
  totals: PaymentTotals | null;
  onAdd: (data: PaymentCreateRequest) => Promise<void>;
  onRemove: (paymentId: string) => Promise<void>;
}

const TIPO_COLORS: Record<string, string> = {
  honorarios: 'bg-blue-100 text-blue-700',
  impuestos: 'bg-amber-100 text-amber-700',
  derechos: 'bg-purple-100 text-purple-700',
  gastos: 'bg-gray-100 text-gray-700',
  otro: 'bg-neutral-100 text-neutral-700',
};

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
  }).format(amount);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function PaymentList({ payments, totals, onAdd, onRemove }: PaymentListProps) {
  const [showForm, setShowForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleAdd = async (data: PaymentCreateRequest) => {
    setIsLoading(true);
    try {
      await onAdd(data);
      setShowForm(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Totals Summary */}
      {totals && totals.total > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card className="p-4 text-center">
            <p className="text-xs text-neutral-500 uppercase">Total</p>
            <p className="text-xl font-bold text-neutral-900">{formatCurrency(totals.total)}</p>
            <p className="text-xs text-neutral-500">{totals.count} pagos</p>
          </Card>
          {Object.entries(totals.by_tipo).map(([tipo, amount]) => (
            <Card key={tipo} className="p-4 text-center">
              <p className="text-xs text-neutral-500 uppercase">
                {PAYMENT_TIPO_LABELS[tipo as keyof typeof PAYMENT_TIPO_LABELS] || tipo}
              </p>
              <p className="text-lg font-semibold text-neutral-900">{formatCurrency(amount)}</p>
            </Card>
          ))}
        </div>
      )}

      {/* Add Button */}
      {!showForm && (
        <div className="flex justify-end">
          <Button onClick={() => setShowForm(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Registrar Pago
          </Button>
        </div>
      )}

      {/* Form */}
      {showForm && (
        <PaymentForm
          onSubmit={handleAdd}
          onCancel={() => setShowForm(false)}
          isLoading={isLoading}
        />
      )}

      {/* Payment List */}
      {payments.length === 0 ? (
        <Card className="p-8">
          <div className="text-center space-y-2">
            <DollarSign className="w-10 h-10 text-neutral-400 mx-auto" />
            <p className="text-neutral-600">No hay pagos registrados</p>
            <p className="text-sm text-neutral-500">
              Registra el primer pago para este expediente
            </p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="divide-y divide-neutral-200">
            {payments.map((payment) => (
              <div key={payment.id} className="p-4 hover:bg-neutral-50 flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={cn(
                        'px-2 py-0.5 text-xs font-medium rounded-full',
                        TIPO_COLORS[payment.tipo] || TIPO_COLORS.otro
                      )}
                    >
                      {PAYMENT_TIPO_LABELS[payment.tipo] || payment.tipo}
                    </span>
                    <span className="text-sm font-medium text-neutral-900">
                      {payment.concepto}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                    <span>{formatDate(payment.fecha_pago)}</span>
                    <span>{PAYMENT_METODO_LABELS[payment.metodo_pago] || payment.metodo_pago}</span>
                    {payment.referencia && <span>Ref: {payment.referencia}</span>}
                    {payment.recibido_por && <span>Recibio: {payment.recibido_por}</span>}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-neutral-900">
                    {formatCurrency(payment.monto)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-neutral-400 hover:text-red-500"
                  onClick={() => onRemove(payment.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
