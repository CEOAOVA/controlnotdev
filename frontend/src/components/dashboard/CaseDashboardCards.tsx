import { Briefcase, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import type { CaseDashboard } from '@/api/types/cases-types';

interface CaseDashboardCardsProps {
  dashboard: CaseDashboard;
}

export function CaseDashboardCards({ dashboard }: CaseDashboardCardsProps) {
  const cards = [
    {
      label: 'Total Expedientes',
      value: dashboard.total_cases,
      icon: Briefcase,
      color: 'text-primary-600',
      bg: 'bg-primary-50',
    },
    {
      label: 'Tramites Vencidos',
      value: dashboard.overdue_tramites,
      icon: AlertTriangle,
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
    {
      label: 'Proximos a Vencer',
      value: dashboard.upcoming_tramites,
      icon: Clock,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
    },
    {
      label: 'Cerrados',
      value: dashboard.by_status['cerrado'] || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.label} className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-600">{card.label}</p>
              <p className="text-2xl font-bold text-neutral-900 mt-1">{card.value}</p>
            </div>
            <div className={`p-2 rounded-lg ${card.bg}`}>
              <card.icon className={`w-5 h-5 ${card.color}`} />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
