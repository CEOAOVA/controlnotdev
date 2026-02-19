/**
 * ReportsPage
 * Dashboard with analytics and summary reports
 */

import { useState, useEffect } from 'react';
import { BarChart3, RefreshCw } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CasesReport } from '@/components/reports/CasesReport';
import { FinancialReport } from '@/components/reports/FinancialReport';
import { TramitesReport } from '@/components/reports/TramitesReport';
import {
  reportsApi,
  type CasesSummary,
  type TramitesSummary,
  type FinancialSummary,
  type ProductivitySummary,
} from '@/api/endpoints/reports';

export function ReportsPage() {
  const [casesSummary, setCasesSummary] = useState<CasesSummary | null>(null);
  const [tramitesSummary, setTramitesSummary] = useState<TramitesSummary | null>(null);
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null);
  const [productivity, setProductivity] = useState<ProductivitySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadAll = async () => {
    setIsLoading(true);
    try {
      const [cases, tramites, financial, prod] = await Promise.all([
        reportsApi.casesSummary(),
        reportsApi.tramitesSummary(),
        reportsApi.financialSummary(),
        reportsApi.productivity(),
      ]);
      setCasesSummary(cases);
      setTramitesSummary(tramites);
      setFinancialSummary(financial);
      setProductivity(prod);
    } catch (err) {
      console.error('Error loading reports:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-primary-600" />
            <h1 className="text-2xl font-bold text-neutral-900">Reportes</h1>
          </div>
          <Button variant="outline" onClick={loadAll} disabled={isLoading} className="gap-2">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>

        {/* Productivity KPIs */}
        {productivity && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="p-4 text-center">
              <p className="text-xs text-neutral-500 uppercase">Total Expedientes</p>
              <p className="text-2xl font-bold">{productivity.total_cases}</p>
            </Card>
            <Card className="p-4 text-center">
              <p className="text-xs text-neutral-500 uppercase">Cerrados</p>
              <p className="text-2xl font-bold text-green-600">{productivity.cerrados}</p>
            </Card>
            <Card className="p-4 text-center">
              <p className="text-xs text-neutral-500 uppercase">Abiertos</p>
              <p className="text-2xl font-bold text-blue-600">{productivity.abiertos}</p>
            </Card>
            <Card className="p-4 text-center">
              <p className="text-xs text-neutral-500 uppercase">Promedio Cierre</p>
              <p className="text-2xl font-bold">{productivity.promedio_dias_cierre} dias</p>
              <p className="text-xs text-neutral-500">Tasa: {productivity.tasa_cierre}%</p>
            </Card>
          </div>
        )}

        {/* Loading skeleton */}
        {isLoading && !casesSummary && (
          <div className="space-y-4">
            <div className="h-48 bg-neutral-200 rounded animate-pulse" />
            <div className="h-48 bg-neutral-200 rounded animate-pulse" />
          </div>
        )}

        {/* Reports Sections */}
        <CasesReport data={casesSummary} />
        <TramitesReport data={tramitesSummary} />
        <FinancialReport data={financialSummary} />
      </div>
    </MainLayout>
  );
}
