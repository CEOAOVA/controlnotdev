/**
 * EventCard
 * Small card for displaying a calendar event
 */

import { cn } from '@/lib/utils';
import type { CalendarEvent } from '@/api/types/calendar-types';
import { EVENT_TIPO_LABELS } from '@/api/types/calendar-types';

interface EventCardProps {
  event: CalendarEvent;
  onClick?: (event: CalendarEvent) => void;
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('es-MX', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function EventCard({ event, onClick }: EventCardProps) {
  return (
    <div
      className={cn(
        'px-2 py-1 rounded text-xs cursor-pointer truncate',
        'hover:opacity-80 transition-opacity'
      )}
      style={{ backgroundColor: event.color + '20', color: event.color, borderLeft: `3px solid ${event.color}` }}
      onClick={() => onClick?.(event)}
      title={`${event.titulo} - ${EVENT_TIPO_LABELS[event.tipo] || event.tipo}`}
    >
      {!event.todo_el_dia && (
        <span className="font-medium">{formatTime(event.fecha_inicio)} </span>
      )}
      <span>{event.titulo}</span>
    </div>
  );
}
