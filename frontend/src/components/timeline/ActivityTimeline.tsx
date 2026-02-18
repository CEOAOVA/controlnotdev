import { format } from 'date-fns';
import { Clock } from 'lucide-react';
import { Card } from '@/components/ui/card';
import type { CaseTimeline } from '@/api/types/cases-types';

interface ActivityTimelineProps {
  timeline: CaseTimeline | null;
}

export function ActivityTimeline({ timeline }: ActivityTimelineProps) {
  if (!timeline || timeline.events.length === 0) {
    return (
      <Card className="p-8">
        <div className="text-center space-y-2">
          <Clock className="w-10 h-10 text-neutral-400 mx-auto" />
          <p className="text-neutral-600">No hay actividad registrada</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-neutral-200" />
        <div className="space-y-4">
          {timeline.events.map((event, index) => (
            <div key={event.id || index} className="relative flex gap-4 pl-10">
              <div className="absolute left-2.5 w-3 h-3 rounded-full bg-primary-500 border-2 border-white" />
              <Card className="flex-1 p-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-neutral-900">{event.description || event.event_type}</p>
                    {event.details && (
                      <p className="text-xs text-neutral-500 mt-1">{event.details}</p>
                    )}
                  </div>
                  {event.created_at && (
                    <span className="text-xs text-neutral-400 whitespace-nowrap">
                      {format(new Date(event.created_at), 'dd/MM/yyyy HH:mm')}
                    </span>
                  )}
                </div>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
