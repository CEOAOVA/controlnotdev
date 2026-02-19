/**
 * CalendarPage
 * Monthly calendar view with event management
 */

import { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { MonthView } from '@/components/calendar/MonthView';
import { EventForm } from '@/components/calendar/EventForm';
import { calendarApi } from '@/api/endpoints/calendar';
import { useToast } from '@/hooks';
import type { CalendarEvent, EventCreateRequest } from '@/api/types/calendar-types';
import { EVENT_TIPO_LABELS } from '@/api/types/calendar-types';

const MONTH_NAMES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

export function CalendarPage() {
  const toast = useToast();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadEvents = useCallback(async () => {
    const start = new Date(year, month, 1).toISOString();
    const end = new Date(year, month + 1, 0, 23, 59, 59).toISOString();
    try {
      const data = await calendarApi.list(start, end);
      setEvents(data);
    } catch (err) {
      console.error('Error loading events:', err);
    }
  }, [year, month]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const goToPrev = () => {
    if (month === 0) { setMonth(11); setYear(year - 1); }
    else setMonth(month - 1);
  };

  const goToNext = () => {
    if (month === 11) { setMonth(0); setYear(year + 1); }
    else setMonth(month + 1);
  };

  const goToToday = () => {
    setYear(now.getFullYear());
    setMonth(now.getMonth());
  };

  const handleDayClick = (date: string) => {
    setSelectedDate(date);
    setShowForm(true);
  };

  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
  };

  const handleCreateEvent = async (data: EventCreateRequest) => {
    setIsLoading(true);
    try {
      await calendarApi.create(data);
      toast.success('Evento creado');
      setShowForm(false);
      loadEvents();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al crear evento');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    try {
      await calendarApi.remove(eventId);
      toast.success('Evento eliminado');
      setSelectedEvent(null);
      loadEvents();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al eliminar evento');
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CalendarIcon className="w-6 h-6 text-primary-600" />
            <h1 className="text-2xl font-bold text-neutral-900">Calendario</h1>
          </div>
          <Button onClick={() => { setSelectedDate(''); setShowForm(true); }} className="gap-2">
            <Plus className="w-4 h-4" />
            Nuevo Evento
          </Button>
        </div>

        {/* Month Navigation */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" onClick={goToPrev}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <h2 className="text-lg font-semibold min-w-[200px] text-center">
              {MONTH_NAMES[month]} {year}
            </h2>
            <Button variant="outline" size="icon" onClick={goToNext}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
          <Button variant="outline" size="sm" onClick={goToToday}>
            Hoy
          </Button>
        </div>

        {/* Event Form */}
        {showForm && (
          <EventForm
            initialDate={selectedDate}
            onSubmit={handleCreateEvent}
            onCancel={() => setShowForm(false)}
            isLoading={isLoading}
          />
        )}

        {/* Event Detail */}
        {selectedEvent && (
          <div className="bg-white border rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">{selectedEvent.titulo}</h3>
              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDeleteEvent(selectedEvent.id)}
                >
                  Eliminar
                </Button>
                <Button variant="outline" size="sm" onClick={() => setSelectedEvent(null)}>
                  Cerrar
                </Button>
              </div>
            </div>
            <div className="text-sm text-neutral-600 space-y-1">
              <p>Tipo: {EVENT_TIPO_LABELS[selectedEvent.tipo] || selectedEvent.tipo}</p>
              <p>Fecha: {new Date(selectedEvent.fecha_inicio).toLocaleString('es-MX')}</p>
              {selectedEvent.fecha_fin && (
                <p>Fin: {new Date(selectedEvent.fecha_fin).toLocaleString('es-MX')}</p>
              )}
              {selectedEvent.descripcion && <p>{selectedEvent.descripcion}</p>}
              {selectedEvent.todo_el_dia && <p>Todo el dia</p>}
            </div>
          </div>
        )}

        {/* Calendar Grid */}
        <MonthView
          year={year}
          month={month}
          events={events}
          onDayClick={handleDayClick}
          onEventClick={handleEventClick}
        />
      </div>
    </MainLayout>
  );
}
