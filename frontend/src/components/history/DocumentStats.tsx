/**
 * DocumentStats Component
 * Dashboard cards showing document statistics
 */

import { FileText, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export interface DocumentStatsData {
  totalDocuments: number;
  byStatus: {
    completed?: number;
    processing?: number;
    error?: number;
    [key: string]: number | undefined;
  };
  byType: {
    [key: string]: number;
  };
}

interface DocumentStatsProps {
  stats: DocumentStatsData;
  isLoading?: boolean;
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

function StatCard({ title, value, icon, color, bgColor }: StatCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-center gap-4">
        <div className={cn('w-12 h-12 rounded-lg flex items-center justify-center', bgColor)}>
          <div className={color}>{icon}</div>
        </div>
        <div>
          <p className="text-sm text-neutral-600">{title}</p>
          <p className="text-2xl font-bold text-neutral-900">{value}</p>
        </div>
      </div>
    </Card>
  );
}

function StatCardSkeleton() {
  return (
    <Card className="p-6 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 bg-neutral-200 rounded-lg" />
        <div className="space-y-2">
          <div className="h-4 bg-neutral-200 rounded w-20" />
          <div className="h-6 bg-neutral-200 rounded w-12" />
        </div>
      </div>
    </Card>
  );
}

export function DocumentStats({ stats, isLoading = false }: DocumentStatsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    );
  }

  const completedCount = stats.byStatus.completed || stats.byStatus.completado || 0;
  const processingCount = stats.byStatus.processing || stats.byStatus.procesando || 0;
  const errorCount = stats.byStatus.error || 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Documentos"
        value={stats.totalDocuments}
        icon={<FileText className="w-6 h-6" />}
        color="text-primary-600"
        bgColor="bg-primary-50"
      />
      <StatCard
        title="Completados"
        value={completedCount}
        icon={<CheckCircle2 className="w-6 h-6" />}
        color="text-success-600"
        bgColor="bg-success-50"
      />
      <StatCard
        title="En Proceso"
        value={processingCount}
        icon={<Clock className="w-6 h-6" />}
        color="text-warning-600"
        bgColor="bg-warning-50"
      />
      <StatCard
        title="Con Errores"
        value={errorCount}
        icon={<AlertTriangle className="w-6 h-6" />}
        color="text-error-600"
        bgColor="bg-error-50"
      />
    </div>
  );
}
