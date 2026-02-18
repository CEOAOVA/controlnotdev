/**
 * Dashboard Page
 * Main landing page with CRM metrics, recent cases, and quick actions
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  FolderOpen,
  Clock,
  TrendingUp,
  ArrowRight,
  Plus,
  AlertCircle,
  Briefcase,
} from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth, useCases } from '@/hooks';
import { STATUS_LABELS, STATUS_COLORS } from '@/api/types/cases-types';

interface MetricCard {
  label: string;
  value: string | number;
  change?: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: 'up' | 'down' | 'neutral';
}

export function Dashboard() {
  const { userName, tenantName } = useAuth();
  const { cases, dashboard, isLoading: _isLoading, error, fetchCases, fetchDashboard } = useCases();
  const [metrics, setMetrics] = useState<MetricCard[]>([]);

  useEffect(() => {
    let isMounted = true;

    const loadDashboardData = async () => {
      try {
        await Promise.all([
          fetchDashboard(),
          fetchCases({ page: 1, page_size: 5 }),
        ]);
      } catch (err) {
        if (isMounted) {
          console.error('Error loading dashboard data:', err);
        }
      }
    };

    loadDashboardData();

    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (dashboard) {
      const activeCount = Object.entries(dashboard.by_status)
        .filter(([key]) => key !== 'cerrado' && key !== 'cancelado')
        .reduce((sum, [, count]) => sum + count, 0);

      setMetrics([
        {
          label: 'Total Expedientes',
          value: dashboard.total_cases,
          icon: Briefcase,
        },
        {
          label: 'En Progreso',
          value: activeCount,
          icon: Clock,
        },
        {
          label: 'Tramites Vencidos',
          value: dashboard.overdue_tramites,
          change: dashboard.overdue_tramites > 0 ? 'Requieren atencion' : 'Todo al dia',
          icon: AlertCircle,
          trend: dashboard.overdue_tramites > 0 ? 'down' : 'up',
        },
        {
          label: 'Proximos a Vencer',
          value: dashboard.upcoming_tramites,
          icon: TrendingUp,
        },
      ]);
    }
  }, [dashboard]);

  const getTrendColor = (trend?: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return 'text-success';
      case 'down':
        return 'text-error';
      default:
        return 'text-neutral-500';
    }
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Welcome Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900">
            Bienvenido, {userName}
          </h1>
          {tenantName && (
            <p className="text-neutral-600 mt-1">
              {tenantName}
            </p>
          )}
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-3">
          <Link to="/generate">
            <Button size="lg" className="gap-2">
              <Plus className="w-5 h-5" />
              Nuevo Documento
            </Button>
          </Link>
          <Link to="/cases">
            <Button variant="outline" size="lg" className="gap-2">
              <Briefcase className="w-5 h-5" />
              Ver Expedientes
            </Button>
          </Link>
          <Link to="/templates">
            <Button variant="outline" size="lg" className="gap-2">
              <FolderOpen className="w-5 h-5" />
              Ver Templates
            </Button>
          </Link>
          <Link to="/history">
            <Button variant="outline" size="lg" className="gap-2">
              <Clock className="w-5 h-5" />
              Ver Historial
            </Button>
          </Link>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {metrics.map((metric, index) => (
            <Card key={index} className="p-4 sm:p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <p className="text-sm text-neutral-600">{metric.label}</p>
                  <p className="text-3xl font-bold text-neutral-900">
                    {metric.value}
                  </p>
                  {metric.change && (
                    <p className={`text-sm ${getTrendColor(metric.trend)}`}>
                      {metric.change}
                    </p>
                  )}
                </div>
                <div className="p-3 bg-primary-50 rounded-lg">
                  <metric.icon className="w-6 h-6 text-primary-600" />
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Semaforo Global */}
        {dashboard?.semaforo_global && (
          <Card className="p-4 sm:p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-4">Semaforo Global de Tramites</h2>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-green-500" />
                <span className="text-sm text-neutral-700">{dashboard.semaforo_global.verde} en tiempo</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-yellow-500" />
                <span className="text-sm text-neutral-700">{dashboard.semaforo_global.amarillo} por vencer</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-red-500" />
                <span className="text-sm text-neutral-700">{dashboard.semaforo_global.rojo} vencidos</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-gray-400" />
                <span className="text-sm text-neutral-700">{dashboard.semaforo_global.gris} sin fecha</span>
              </div>
            </div>
          </Card>
        )}

        {/* Recent Cases */}
        <div>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
            <h2 className="text-xl sm:text-2xl font-bold text-neutral-900">
              Expedientes Recientes
            </h2>
            <Link to="/cases">
              <Button variant="ghost" className="gap-2">
                Ver todos
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {cases.length === 0 ? (
            <Card className="p-6 sm:p-12">
              <div className="text-center space-y-3">
                <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
                  <Briefcase className="w-8 h-8 text-neutral-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900">
                    No hay expedientes recientes
                  </h3>
                  <p className="text-neutral-600 mt-1">
                    Comienza creando tu primer expediente
                  </p>
                </div>
                <Link to="/cases">
                  <Button className="gap-2 mt-4">
                    <Plus className="w-4 h-4" />
                    Nuevo Expediente
                  </Button>
                </Link>
              </div>
            </Card>
          ) : (
            <Card>
              <div className="divide-y divide-neutral-200">
                {cases.slice(0, 5).map((caseItem) => (
                  <Link
                    key={caseItem.id}
                    to={`/cases/${caseItem.id}`}
                    className="block p-4 hover:bg-neutral-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-primary-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-neutral-900 truncate">
                            {caseItem.case_number}
                          </p>
                          <p className="text-sm text-neutral-600">
                            {caseItem.document_type} {caseItem.description ? `- ${caseItem.description}` : ''}
                          </p>
                        </div>
                      </div>
                      <Badge className={STATUS_COLORS[caseItem.status]}>
                        {STATUS_LABELS[caseItem.status]}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Status Breakdown */}
        {dashboard && Object.keys(dashboard.by_status).length > 0 && (
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-neutral-900 mb-4">
              Por Estado
            </h2>
            <Card className="p-4 sm:p-6">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {Object.entries(dashboard.by_status)
                  .filter(([, count]) => count > 0)
                  .map(([status, count]) => (
                    <div key={status} className="flex items-center justify-between p-2 rounded-lg bg-neutral-50">
                      <Badge className={STATUS_COLORS[status as keyof typeof STATUS_COLORS] || 'bg-gray-100 text-gray-700'}>
                        {STATUS_LABELS[status as keyof typeof STATUS_LABELS] || status}
                      </Badge>
                      <span className="font-semibold text-neutral-900">{count}</span>
                    </div>
                  ))}
              </div>
            </Card>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
