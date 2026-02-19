/**
 * MonthView
 * Monthly calendar grid with events
 */

import { cn } from '@/lib/utils';
import { EventCard } from './EventCard';
import type { CalendarEvent } from '@/api/types/calendar-types';

interface MonthViewProps {
  year: number;
  month: number;
  events: CalendarEvent[];
  onDayClick: (date: string) => void;
  onEventClick: (event: CalendarEvent) => void;
}

const DAY_NAMES = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];

function getDaysInMonth(year: number, month: number): Date[] {
  const days: Date[] = [];
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  // Get Monday of the week containing the 1st
  const startDate = new Date(firstDay);
  const dayOfWeek = startDate.getDay();
  const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Monday-based
  startDate.setDate(startDate.getDate() - diff);

  // Fill until we have at least the whole month and complete the week
  const current = new Date(startDate);
  while (current <= lastDay || current.getDay() !== 1) {
    days.push(new Date(current));
    current.setDate(current.getDate() + 1);
    if (days.length > 42) break; // Safety: max 6 weeks
  }

  return days;
}

function dateKey(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function MonthView({ year, month, events, onDayClick, onEventClick }: MonthViewProps) {
  const days = getDaysInMonth(year, month);
  const today = dateKey(new Date());

  // Group events by date
  const eventsByDate: Record<string, CalendarEvent[]> = {};
  events.forEach((event) => {
    const key = event.fecha_inicio.split('T')[0];
    if (!eventsByDate[key]) eventsByDate[key] = [];
    eventsByDate[key].push(event);
  });

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Day headers */}
      <div className="grid grid-cols-7 bg-neutral-50 border-b">
        {DAY_NAMES.map((name) => (
          <div key={name} className="px-2 py-2 text-center text-xs font-medium text-neutral-500">
            {name}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7">
        {days.map((date, idx) => {
          const key = dateKey(date);
          const isCurrentMonth = date.getMonth() === month;
          const isToday = key === today;
          const dayEvents = eventsByDate[key] || [];

          return (
            <div
              key={idx}
              className={cn(
                'min-h-[100px] border-b border-r p-1 cursor-pointer hover:bg-neutral-50',
                !isCurrentMonth && 'bg-neutral-50/50 text-neutral-400'
              )}
              onClick={() => onDayClick(key)}
            >
              <div className="flex items-center justify-between">
                <span
                  className={cn(
                    'text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full',
                    isToday && 'bg-primary-500 text-white'
                  )}
                >
                  {date.getDate()}
                </span>
              </div>
              <div className="space-y-0.5 mt-1">
                {dayEvents.slice(0, 3).map((event) => (
                  <EventCard
                    key={event.id}
                    event={event}
                    onClick={(e) => {
                      e.stopPropagation?.();
                      onEventClick(event);
                    }}
                  />
                ))}
                {dayEvents.length > 3 && (
                  <p className="text-xs text-neutral-500 px-1">+{dayEvents.length - 3} mas</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
