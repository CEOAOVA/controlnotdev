import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CASE_STATUSES, STATUS_LABELS } from '@/api/types/cases-types';
import type { CaseStatus, CasePriority } from '@/api/types/cases-types';
import type { DocumentType } from '@/types';

export interface CaseFiltersState {
  search: string;
  status: CaseStatus | 'all';
  document_type: DocumentType | 'all';
  priority: CasePriority | 'all';
}

interface CaseFiltersProps {
  onFiltersChange: (filters: CaseFiltersState) => void;
  isLoading?: boolean;
}

const documentTypes: { value: DocumentType | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos los tipos' },
  { value: 'compraventa', label: 'Compraventa' },
  { value: 'donacion', label: 'Donacion' },
  { value: 'testamento', label: 'Testamento' },
  { value: 'poder', label: 'Poder' },
  { value: 'sociedad', label: 'Sociedad' },
  { value: 'cancelacion', label: 'Cancelacion' },
];

const priorities: { value: CasePriority | 'all'; label: string }[] = [
  { value: 'all', label: 'Todas las prioridades' },
  { value: 'baja', label: 'Baja' },
  { value: 'normal', label: 'Normal' },
  { value: 'alta', label: 'Alta' },
  { value: 'urgente', label: 'Urgente' },
];

export function CaseFilters({ onFiltersChange, isLoading = false }: CaseFiltersProps) {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<CaseStatus | 'all'>('all');
  const [documentType, setDocumentType] = useState<DocumentType | 'all'>('all');
  const [priority, setPriority] = useState<CasePriority | 'all'>('all');

  useEffect(() => {
    const timer = setTimeout(() => {
      onFiltersChange({
        search,
        status,
        document_type: documentType,
        priority,
      });
    }, 300);

    return () => clearTimeout(timer);
  }, [search, status, documentType, priority, onFiltersChange]);

  const hasActiveFilters = search !== '' || status !== 'all' || documentType !== 'all' || priority !== 'all';

  const handleClear = () => {
    setSearch('');
    setStatus('all');
    setDocumentType('all');
    setPriority('all');
  };

  return (
    <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
        <Input
          type="search"
          placeholder="Buscar por numero, descripcion..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          disabled={isLoading}
          className="pl-9 pr-9"
        />
        {search && (
          <button
            type="button"
            onClick={() => setSearch('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center gap-3 w-full sm:w-auto">
        <Select
          value={status}
          onValueChange={(v) => setStatus(v as CaseStatus | 'all')}
          disabled={isLoading}
        >
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos los estados</SelectItem>
            {CASE_STATUSES.map((s) => (
              <SelectItem key={s} value={s}>{STATUS_LABELS[s]}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={documentType}
          onValueChange={(v) => setDocumentType(v as DocumentType | 'all')}
          disabled={isLoading}
        >
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {documentTypes.map((dt) => (
              <SelectItem key={dt.value} value={dt.value}>{dt.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={priority}
          onValueChange={(v) => setPriority(v as CasePriority | 'all')}
          disabled={isLoading}
        >
          <SelectTrigger className="w-full sm:w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {priorities.map((p) => (
              <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={handleClear} disabled={isLoading} className="gap-1">
            <X className="w-4 h-4" />
            Limpiar
          </Button>
        )}
      </div>
    </div>
  );
}
