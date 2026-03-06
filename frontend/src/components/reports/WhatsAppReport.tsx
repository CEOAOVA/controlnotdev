/**
 * WhatsAppReport
 * WhatsApp activity summary: messages, conversations, extractions, commands
 */

import { Card } from '@/components/ui/card';
import type { WhatsAppSummary } from '@/api/endpoints/reports';

interface WhatsAppReportProps {
  data: WhatsAppSummary | null;
}

function BreakdownTable({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);

  if (entries.length === 0) return null;

  return (
    <Card className="p-4">
      <h4 className="text-sm font-semibold text-neutral-700 mb-3">{title}</h4>
      <div className="space-y-2">
        {entries.map(([key, value]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-sm text-neutral-600 capitalize">{key.replace(/_/g, ' ')}</span>
            <div className="flex items-center gap-2">
              <div className="w-24 bg-neutral-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${total > 0 ? (value / total) * 100 : 0}%` }}
                />
              </div>
              <span className="text-sm font-medium w-8 text-right">{value}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export function WhatsAppReport({ data }: WhatsAppReportProps) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-lg font-semibold">WhatsApp</h3>
        <span className="text-sm text-neutral-500">{data.messages.total} mensajes</span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Total Mensajes</p>
          <p className="text-2xl font-bold">{data.messages.total}</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Conversaciones Abiertas</p>
          <p className="text-2xl font-bold text-blue-600">
            {data.conversations.by_status['open'] || 0}
          </p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Mensajes Fallidos</p>
          <p className="text-2xl font-bold text-red-600">{data.messages.failed_count}</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Sin Leer</p>
          <p className="text-2xl font-bold text-yellow-600">{data.conversations.total_unread}</p>
        </Card>
      </div>

      {/* Message Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <BreakdownTable title="Por Remitente" data={data.messages.by_sender_type} />
        <BreakdownTable title="Por Tipo de Mensaje" data={data.messages.by_message_type} />
        <BreakdownTable title="Estado de Entrega" data={data.messages.by_status} />
      </div>

      {/* Extractions */}
      {data.extractions.total > 0 && (
        <Card className="p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">
            Extracciones via WhatsApp
            <span className="ml-2 text-xs font-normal text-neutral-500">
              {data.extractions.total} total | Confianza promedio: {Math.round(data.extractions.avg_confidence * 100)}%
            </span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-neutral-500 mb-2">Por Tipo de Documento</p>
              <div className="space-y-1">
                {Object.entries(data.extractions.by_document_type).sort((a, b) => b[1] - a[1]).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="text-sm font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-2">Por Estado</p>
              <div className="space-y-1">
                {Object.entries(data.extractions.by_status).sort((a, b) => b[1] - a[1]).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="text-sm font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Commands */}
      {data.commands.total > 0 && (
        <Card className="p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">
            Actividad Staff
            <span className="ml-2 text-xs font-normal text-neutral-500">
              {data.commands.total} comandos
            </span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-neutral-500 mb-2">Top Comandos</p>
              <div className="space-y-1">
                {Object.entries(data.commands.top_commands).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600 font-mono">{key}</span>
                    <span className="text-sm font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-2">Por Staff</p>
              <div className="space-y-1">
                {Object.entries(data.commands.by_staff).sort((a, b) => b[1] - a[1]).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">{key}</span>
                    <span className="text-sm font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
