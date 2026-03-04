/**
 * NotificationRulesPanel
 * CRUD panel for managing WhatsApp notification rules
 */

import { useState, useEffect } from 'react';
import { Bell, Plus, Trash2, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import { useToast } from '@/hooks/useToast';
import type { WANotificationRule } from '@/api/types/whatsapp-types';

const EVENT_TYPES = [
  { value: 'case_created', label: 'Caso Creado' },
  { value: 'status_change', label: 'Cambio de Estado' },
  { value: 'tramite_vencido', label: 'Tramite Vencido' },
  { value: 'checklist_complete', label: 'Checklist Completo' },
  { value: 'payment_received', label: 'Pago Recibido' },
];

export function NotificationRulesPanel() {
  const [rules, setRules] = useState<WANotificationRule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const toast = useToast();

  // New rule form
  const [newEventType, setNewEventType] = useState('status_change');
  const [newMessageText, setNewMessageText] = useState('');
  const [newNotifyStaff, setNewNotifyStaff] = useState(false);

  const loadRules = async () => {
    setIsLoading(true);
    try {
      const data = await whatsappApi.listNotificationRules();
      setRules(data);
    } catch (err) {
      console.error('Error loading notification rules:', err);
      toast.error('Error al cargar reglas de notificacion');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleAdd = async () => {
    if (!newEventType) return;
    try {
      await whatsappApi.createNotificationRule({
        event_type: newEventType,
        is_active: true,
        notify_staff: newNotifyStaff,
        message_text: newMessageText || undefined,
      });
      setNewEventType('status_change');
      setNewMessageText('');
      setNewNotifyStaff(false);
      setIsAdding(false);
      toast.success('Regla creada');
      loadRules();
    } catch (err) {
      console.error('Error creating rule:', err);
      toast.error('Error al crear regla');
    }
  };

  const handleToggleActive = async (rule: WANotificationRule) => {
    try {
      await whatsappApi.updateNotificationRule(rule.id, {
        is_active: !rule.is_active,
      });
      toast.success(rule.is_active ? 'Regla desactivada' : 'Regla activada');
      loadRules();
    } catch (err) {
      console.error('Error toggling rule:', err);
      toast.error('Error al cambiar estado de regla');
    }
  };

  const handleToggleStaff = async (rule: WANotificationRule) => {
    try {
      await whatsappApi.updateNotificationRule(rule.id, {
        notify_staff: !rule.notify_staff,
      });
      toast.success(rule.notify_staff ? 'Notificacion a staff desactivada' : 'Notificacion a staff activada');
      loadRules();
    } catch (err) {
      console.error('Error toggling rule staff:', err);
      toast.error('Error al cambiar notificacion de staff');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Eliminar esta regla de notificacion?')) return;
    try {
      await whatsappApi.deleteNotificationRule(id);
      toast.success('Regla eliminada');
      loadRules();
    } catch (err) {
      console.error('Error deleting rule:', err);
      toast.error('Error al eliminar regla');
    }
  };

  const getEventLabel = (eventType: string) =>
    EVENT_TYPES.find((e) => e.value === eventType)?.label || eventType;

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-amber-600" />
          <h3 className="font-semibold text-lg">Reglas de Notificacion</h3>
        </div>
        <Button size="sm" onClick={() => setIsAdding(!isAdding)} className="gap-1">
          <Plus className="w-4 h-4" />
          Agregar
        </Button>
      </div>

      {isAdding && (
        <div className="flex flex-wrap gap-2 mb-4 p-3 bg-neutral-50 rounded-lg">
          <Select value={newEventType} onValueChange={setNewEventType}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {EVENT_TYPES.map((e) => (
                <SelectItem key={e.value} value={e.value}>{e.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input
            placeholder="Mensaje (opcional)"
            value={newMessageText}
            onChange={(e) => setNewMessageText(e.target.value)}
            className="w-64"
          />
          <label className="flex items-center gap-2 text-sm">
            <Switch checked={newNotifyStaff} onCheckedChange={setNewNotifyStaff} />
            Notificar Staff
          </label>
          <Button size="sm" onClick={handleAdd}>
            <Check className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setIsAdding(false)}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      )}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Evento</TableHead>
            <TableHead>Mensaje</TableHead>
            <TableHead>Activa</TableHead>
            <TableHead>Notif. Staff</TableHead>
            <TableHead className="w-16">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-8 text-neutral-500">
                Cargando...
              </TableCell>
            </TableRow>
          ) : rules.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-8 text-neutral-500">
                No hay reglas de notificacion configuradas
              </TableCell>
            </TableRow>
          ) : (
            rules.map((rule) => (
              <TableRow key={rule.id}>
                <TableCell>
                  <Badge variant="outline">{getEventLabel(rule.event_type)}</Badge>
                </TableCell>
                <TableCell className="text-sm text-neutral-600 max-w-xs truncate">
                  {rule.message_text || (rule.template_id ? `Template: ${rule.template_id}` : '—')}
                </TableCell>
                <TableCell>
                  <Switch
                    checked={rule.is_active}
                    onCheckedChange={() => handleToggleActive(rule)}
                  />
                </TableCell>
                <TableCell>
                  <Switch
                    checked={rule.notify_staff}
                    onCheckedChange={() => handleToggleStaff(rule)}
                  />
                </TableCell>
                <TableCell>
                  <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => handleDelete(rule.id)}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Card>
  );
}
