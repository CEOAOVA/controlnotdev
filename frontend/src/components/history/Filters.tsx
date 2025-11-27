/**
 * Filters Component
 * Search and filter controls for document history
 */

import { useState, useEffect } from 'react';
import { Search, Filter, X, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import type { DocumentType } from '@/store';

export interface DocumentFilters {
  search: string;
  type: DocumentType | 'all';
  status: 'completed' | 'processing' | 'error' | 'all';
  dateFrom: string;
  dateTo: string;
}

interface FiltersProps {
  onFiltersChange: (filters: DocumentFilters) => void;
  isLoading?: boolean;
}

const documentTypes: { value: DocumentType | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos los tipos' },
  { value: 'compraventa', label: 'Compraventa' },
  { value: 'donacion', label: 'Donación' },
  { value: 'testamento', label: 'Testamento' },
  { value: 'poder', label: 'Poder' },
  { value: 'sociedad', label: 'Sociedad' },
];

const statusOptions: { value: 'completed' | 'processing' | 'error' | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos los estados' },
  { value: 'completed', label: 'Completado' },
  { value: 'processing', label: 'Procesando' },
  { value: 'error', label: 'Error' },
];

export function Filters({ onFiltersChange, isLoading = false }: FiltersProps) {
  const [search, setSearch] = useState('');
  const [type, setType] = useState<DocumentType | 'all'>('all');
  const [status, setStatus] = useState<'completed' | 'processing' | 'error' | 'all'>('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Count active filters (excluding search)
  const activeFiltersCount = [
    type !== 'all',
    status !== 'all',
    dateFrom !== '',
    dateTo !== '',
  ].filter(Boolean).length;

  // Emit filters on change (debounced for search)
  useEffect(() => {
    const timer = setTimeout(() => {
      onFiltersChange({ search, type, status, dateFrom, dateTo });
    }, 300); // 300ms debounce for search

    return () => clearTimeout(timer);
  }, [search, type, status, dateFrom, dateTo, onFiltersChange]);

  const handleClearFilters = () => {
    setSearch('');
    setType('all');
    setStatus('all');
    setDateFrom('');
    setDateTo('');
  };

  const hasActiveFilters = search !== '' || activeFiltersCount > 0;

  return (
    <div className="space-y-4">
      {/* Main Filters Row */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <Input
            type="search"
            placeholder="Buscar por nombre o ID..."
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

        {/* Quick Filters */}
        <div className="flex items-center gap-3">
          {/* Status Filter */}
          <Select
            value={status}
            onValueChange={(value) => setStatus(value as typeof status)}
            disabled={isLoading}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Type Filter */}
          <Select
            value={type}
            onValueChange={(value) => setType(value as typeof type)}
            disabled={isLoading}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {documentTypes.map((docType) => (
                <SelectItem key={docType.value} value={docType.value}>
                  {docType.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Toggle Advanced Filters */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowAdvanced(!showAdvanced)}
            disabled={isLoading}
            className="relative"
          >
            <Filter className="w-4 h-4" />
            {activeFiltersCount > 0 && (
              <Badge
                variant="default"
                className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
              >
                {activeFiltersCount}
              </Badge>
            )}
          </Button>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearFilters}
              disabled={isLoading}
              className="gap-1"
            >
              <X className="w-4 h-4" />
              Limpiar
            </Button>
          )}
        </div>
      </div>

      {/* Advanced Filters Panel */}
      {showAdvanced && (
        <Card className="p-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-neutral-900">
                Filtros Avanzados
              </h3>
              <button
                type="button"
                onClick={() => setShowAdvanced(false)}
                className="text-neutral-400 hover:text-neutral-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Date From */}
              <div>
                <Label htmlFor="date-from" className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Desde
                </Label>
                <Input
                  id="date-from"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  disabled={isLoading}
                  max={dateTo || undefined}
                  className="mt-2"
                />
              </div>

              {/* Date To */}
              <div>
                <Label htmlFor="date-to" className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Hasta
                </Label>
                <Input
                  id="date-to"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  disabled={isLoading}
                  min={dateFrom || undefined}
                  className="mt-2"
                />
              </div>
            </div>

            {/* Active Filters Summary */}
            {activeFiltersCount > 0 && (
              <div className="pt-4 border-t border-neutral-200">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm text-neutral-600">
                    Filtros activos:
                  </span>
                  {type !== 'all' && (
                    <Badge variant="secondary" className="gap-1">
                      Tipo: {documentTypes.find((t) => t.value === type)?.label}
                      <button
                        type="button"
                        onClick={() => setType('all')}
                        className="hover:text-neutral-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  )}
                  {status !== 'all' && (
                    <Badge variant="secondary" className="gap-1">
                      Estado: {statusOptions.find((s) => s.value === status)?.label}
                      <button
                        type="button"
                        onClick={() => setStatus('all')}
                        className="hover:text-neutral-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  )}
                  {dateFrom && (
                    <Badge variant="secondary" className="gap-1">
                      Desde: {new Date(dateFrom).toLocaleDateString()}
                      <button
                        type="button"
                        onClick={() => setDateFrom('')}
                        className="hover:text-neutral-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  )}
                  {dateTo && (
                    <Badge variant="secondary" className="gap-1">
                      Hasta: {new Date(dateTo).toLocaleDateString()}
                      <button
                        type="button"
                        onClick={() => setDateTo('')}
                        className="hover:text-neutral-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
