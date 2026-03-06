/**
 * TemplatesReport
 * Templates and generated documents summary
 */

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText } from 'lucide-react';
import type { TemplatesSummary } from '@/api/endpoints/reports';

interface TemplatesReportProps {
  data: TemplatesSummary | null;
  onGenerate: (templateId: string, tipoDocumento: string) => void;
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
                  className="bg-purple-500 h-2 rounded-full"
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

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('es-MX', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return '-';
  }
}

export function TemplatesReport({ data, onGenerate }: TemplatesReportProps) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-lg font-semibold">Plantillas Word</h3>
        <span className="text-sm text-neutral-500">{data.templates.total} plantillas</span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Total Plantillas</p>
          <p className="text-2xl font-bold">{data.templates.total}</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Documentos Generados</p>
          <p className="text-2xl font-bold text-purple-600">{data.documents.total_generated}</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-neutral-500 uppercase">Confianza Promedio</p>
          <p className="text-2xl font-bold">
            {data.documents.avg_confidence > 0
              ? `${Math.round(data.documents.avg_confidence * 100)}%`
              : 'N/A'}
          </p>
        </Card>
      </div>

      {/* Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BreakdownTable title="Plantillas por Tipo de Documento" data={data.templates.by_document_type} />
        <BreakdownTable title="Documentos por Estado" data={data.documents.by_status} />
      </div>

      {/* Templates Table */}
      {data.templates.list.length > 0 && (
        <Card className="p-4 overflow-x-auto">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Detalle de Plantillas</h4>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-neutral-500">
                <th className="pb-2 pr-4">Nombre</th>
                <th className="pb-2 pr-4">Tipo</th>
                <th className="pb-2 pr-4 text-center">Placeholders</th>
                <th className="pb-2 pr-4 text-center">Docs Generados</th>
                <th className="pb-2 pr-4">Ultima Vez</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {data.templates.list
                .sort((a, b) => b.documents_generated - a.documents_generated)
                .map((tpl) => (
                  <tr key={tpl.id} className="border-b last:border-0">
                    <td className="py-2 pr-4 font-medium text-neutral-800">{tpl.nombre}</td>
                    <td className="py-2 pr-4 capitalize text-neutral-600">
                      {tpl.tipo_documento.replace(/_/g, ' ')}
                    </td>
                    <td className="py-2 pr-4 text-center">{tpl.total_placeholders}</td>
                    <td className="py-2 pr-4 text-center font-medium">{tpl.documents_generated}</td>
                    <td className="py-2 pr-4 text-neutral-500">{formatDate(tpl.last_used_at)}</td>
                    <td className="py-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-1"
                        onClick={() => onGenerate(tpl.id, tpl.tipo_documento)}
                      >
                        <FileText className="w-3 h-3" />
                        Generar
                      </Button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
