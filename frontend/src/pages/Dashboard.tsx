/**
 * Dashboard Page
 * Main landing page with metrics, recent documents, and quick actions
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
} from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth, useCases } from '@/hooks';
import { format } from 'date-fns';

interface MetricCard {
  label: string;
  value: string | number;
  change?: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: 'up' | 'down' | 'neutral';
}

interface RecentDocument {
  id: string;
  name: string;
  type: string;
  date: string;
  status: 'completed' | 'processing' | 'error';
}

export function Dashboard() {
  const { userName, tenantName } = useAuth();
  const { cases, stats, isLoading: _isLoading, error, fetchCases, fetchStats } = useCases();
  const [metrics, setMetrics] = useState<MetricCard[]>([]);

  // Fetch dashboard data - solo al montar (sin dependencias para evitar loop)
  useEffect(() => {
    let isMounted = true;

    const loadDashboardData = async () => {
      try {
        await Promise.all([
          fetchStats(),
          fetchCases({ page: 1, per_page: 5, sort_by: 'created_at', sort_order: 'desc' }),
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

  // Update metrics when stats change
  useEffect(() => {
    if (stats) {
      setMetrics([
        {
          label: 'Total Casos',
          value: stats.total_cases,
          icon: FileText,
        },
        {
          label: 'En Progreso',
          value: stats.in_progress,
          icon: Clock,
        },
        {
          label: 'Completados Este Mes',
          value: stats.completed_this_month,
          change: `${stats.completed_this_month} documentos`,
          icon: TrendingUp,
          trend: 'up',
        },
        {
          label: 'Borradores',
          value: stats.by_status.draft || 0,
          icon: FolderOpen,
        },
      ]);
    }
  }, [stats]);

  // Convert cases to recent documents format
  const recentDocuments: RecentDocument[] = cases.slice(0, 5).map((caseItem) => ({
    id: caseItem.id,
    name: caseItem.title,
    type: caseItem.type,
    date: format(new Date(caseItem.created_at), 'dd/MM/yyyy HH:mm'),
    status: caseItem.status === 'completed' ? 'completed' :
            caseItem.status === 'in_progress' ? 'processing' : 'error',
  }));

  const getStatusColor = (status: RecentDocument['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-success/10 text-success-700 border-success/20';
      case 'processing':
        return 'bg-warning/10 text-warning-700 border-warning/20';
      case 'error':
        return 'bg-error/10 text-error-700 border-error/20';
    }
  };

  const getStatusLabel = (status: RecentDocument['status']) => {
    switch (status) {
      case 'completed':
        return 'Completado';
      case 'processing':
        return 'Procesando';
      case 'error':
        return 'Error';
    }
  };

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
          <h1 className="text-3xl font-bold text-neutral-900">
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <Card key={index} className="p-6">
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

        {/* Recent Documents */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-neutral-900">
              Documentos Recientes
            </h2>
            <Link to="/history">
              <Button variant="ghost" className="gap-2">
                Ver todos
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {recentDocuments.length === 0 ? (
            <Card className="p-12">
              <div className="text-center space-y-3">
                <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
                  <FileText className="w-8 h-8 text-neutral-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900">
                    No hay documentos recientes
                  </h3>
                  <p className="text-neutral-600 mt-1">
                    Comienza generando tu primer documento
                  </p>
                </div>
                <Link to="/generate">
                  <Button className="gap-2 mt-4">
                    <Plus className="w-4 h-4" />
                    Generar Documento
                  </Button>
                </Link>
              </div>
            </Card>
          ) : (
            <Card>
              <div className="divide-y divide-neutral-200">
                {recentDocuments.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-4 hover:bg-neutral-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-primary-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-neutral-900 truncate">
                            {doc.name}
                          </p>
                          <p className="text-sm text-neutral-600">
                            {doc.type} • {doc.date}
                          </p>
                        </div>
                      </div>
                      <Badge
                        className={getStatusColor(doc.status)}
                      >
                        {getStatusLabel(doc.status)}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Activity Feed (Placeholder) */}
        <div>
          <h2 className="text-2xl font-bold text-neutral-900 mb-4">
            Actividad Reciente
          </h2>
          <Card className="p-6">
            <div className="text-center text-neutral-600">
              <Clock className="w-12 h-12 mx-auto mb-3 text-neutral-400" />
              <p>No hay actividad reciente</p>
            </div>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
