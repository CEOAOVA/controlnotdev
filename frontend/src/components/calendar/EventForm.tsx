/**
 * EventForm
 * Dialog to create/edit a calendar event
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { X } from 'lucide-react';
import type { EventCreateRequest, EventTipo } from '@/api/types/calendar-types';
import { EVENT_TIPO_LABELS, EVENT_TIPO_COLORS } from '@/api/types/calendar-types';

interface EventFormProps {
  initialDate?: string;
  onSubmit: (data: EventCreateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function EventForm({ initialDate, onSubmit, onCancel, isLoading }: EventFormProps) {
  const [titulo, setTitulo] = useState('');
  const [tipo, setTipo] = useState<EventTipo>('cita');
  const [descripcion, setDescripcion] = useState('');
  const [fechaInicio, setFechaInicio] = useState(initialDate || '');
  const [horaInicio, setHoraInicio] = useState('09:00');
  const [fechaFin, setFechaFin] = useState('');
  const [horaFin, setHoraFin] = useState('10:00');
  const [todoElDia, setTodoElDia] = useState(false);
  const [color, setColor] = useState(EVENT_TIPO_COLORS.cita);

  const handleTipoChange = (newTipo: EventTipo) => {
    setTipo(newTipo);
    setColor(EVENT_TIPO_COLORS[newTipo] || EVENT_TIPO_COLORS.otro);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titulo.trim() || !fechaInicio) return;

    const fecha_inicio = todoElDia
      ? `${fechaInicio}T00:00:00`
      : `${fechaInicio}T${horaInicio}:00`;

    const data: EventCreateRequest = {
      titulo: titulo.trim(),
      tipo,
      color,
      todo_el_dia: todoElDia,
      fecha_inicio,
    };

    if (descripcion.trim()) data.descripcion = descripcion.trim();
    if (fechaFin) {
      data.fecha_fin = todoElDia
        ? `${fechaFin}T23:59:59`
        : `${fechaFin}T${horaFin}:00`;
    }

    await onSubmit(data);
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Nuevo Evento</h3>
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <X className="w-4 h-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2 md:col-span-2">
            <Label>Titulo *</Label>
            <Input
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              placeholder="Ej: Firma de escritura"
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Tipo</Label>
            <Select value={tipo} onValueChange={(v) => handleTipoChange(v as EventTipo)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(EVENT_TIPO_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Color</Label>
            <Input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="h-10 w-full"
            />
          </div>

          <div className="space-y-2">
            <Label>Fecha inicio *</Label>
            <Input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              required
            />
          </div>

          {!todoElDia && (
            <div className="space-y-2">
              <Label>Hora inicio</Label>
              <Input
                type="time"
                value={horaInicio}
                onChange={(e) => setHoraInicio(e.target.value)}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label>Fecha fin</Label>
            <Input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
            />
          </div>

          {!todoElDia && (
            <div className="space-y-2">
              <Label>Hora fin</Label>
              <Input
                type="time"
                value={horaFin}
                onChange={(e) => setHoraFin(e.target.value)}
              />
            </div>
          )}

          <div className="flex items-center gap-2 md:col-span-2">
            <input
              type="checkbox"
              id="todoElDia"
              checked={todoElDia}
              onChange={(e) => setTodoElDia(e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="todoElDia">Todo el dia</Label>
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label>Descripcion</Label>
            <Input
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              placeholder="Detalles del evento..."
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading || !titulo.trim() || !fechaInicio}>
            {isLoading ? 'Creando...' : 'Crear Evento'}
          </Button>
        </div>
      </form>
    </Card>
  );
}
