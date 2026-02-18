import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { Briefcase } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { CaseStatusBadge } from './CaseStatusBadge';
import { CasePriorityBadge } from './CasePriorityBadge';
import type { Case } from '@/api/types/cases-types';

interface CaseTableProps {
  cases: Case[];
  isLoading?: boolean;
}

export function CaseTable({ cases, isLoading = false }: CaseTableProps) {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <Card>
        <div className="divide-y divide-neutral-200">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="p-4 animate-pulse">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-neutral-200 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-neutral-200 rounded w-1/3" />
                  <div className="h-3 bg-neutral-200 rounded w-1/4" />
                </div>
                <div className="w-20 h-6 bg-neutral-200 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (cases.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
            <Briefcase className="w-8 h-8 text-neutral-400" />
          </div>
          <h3 className="text-lg font-semibold text-neutral-900">No hay expedientes</h3>
          <p className="text-neutral-600">Los expedientes creados apareceran aqui</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">Expediente</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">Tipo</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">Estado</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">Prioridad</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">Fecha</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-600 uppercase tracking-wider">Asignado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {cases.map((c) => (
              <tr
                key={c.id}
                className="hover:bg-neutral-50 transition-colors cursor-pointer"
                onClick={() => navigate(`/cases/${c.id}`)}
              >
                <td className="px-6 py-4">
                  <div>
                    <p className="font-medium text-neutral-900">{c.case_number}</p>
                    <p className="text-xs text-neutral-500 truncate max-w-[200px]">{c.description || '-'}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm capitalize text-neutral-700">{c.document_type}</span>
                </td>
                <td className="px-6 py-4">
                  <CaseStatusBadge status={c.status} />
                </td>
                <td className="px-6 py-4">
                  {c.priority ? <CasePriorityBadge priority={c.priority} /> : <span className="text-neutral-400">-</span>}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-neutral-900">{format(new Date(c.created_at), 'dd/MM/yyyy')}</div>
                  <div className="text-xs text-neutral-500">{format(new Date(c.created_at), 'HH:mm')}</div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-neutral-700">{c.assigned_to || '-'}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden divide-y divide-neutral-200">
        {cases.map((c) => (
          <div
            key={c.id}
            className="p-4 hover:bg-neutral-50 transition-colors cursor-pointer"
            onClick={() => navigate(`/cases/${c.id}`)}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-neutral-900">{c.case_number}</p>
                <p className="text-sm text-neutral-600 capitalize">{c.document_type}</p>
                <div className="flex items-center gap-2 mt-2">
                  <CaseStatusBadge status={c.status} />
                  {c.priority && <CasePriorityBadge priority={c.priority} />}
                </div>
                <p className="text-xs text-neutral-500 mt-2">
                  {format(new Date(c.created_at), 'dd/MM/yyyy HH:mm')}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
