/**
 * StaffPhoneManager
 * CRUD table for managing staff WhatsApp phone numbers
 */

import { useState, useEffect } from 'react';
import { Phone, Plus, Trash2, Edit2, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
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
import { Switch } from '@/components/ui/switch';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import { useToast } from '@/hooks/useToast';
import type { WAStaffPhone, StaffRole } from '@/api/types/whatsapp-types';

const ROLES: { value: StaffRole; label: string }[] = [
  { value: 'notario', label: 'Notario' },
  { value: 'asistente', label: 'Asistente' },
  { value: 'abogado', label: 'Abogado' },
  { value: 'admin', label: 'Admin' },
];

export function StaffPhoneManager() {
  const [phones, setPhones] = useState<WAStaffPhone[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const toast = useToast();

  // New phone form
  const [newPhone, setNewPhone] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState<StaffRole>('asistente');

  // Edit form
  const [editName, setEditName] = useState('');
  const [editRole, setEditRole] = useState<StaffRole>('asistente');

  const loadPhones = async () => {
    setIsLoading(true);
    try {
      const data = await whatsappApi.listStaffPhones();
      setPhones(data);
    } catch (err) {
      console.error('Error loading staff phones:', err);
      toast.error('Error al cargar telefonos de staff');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPhones();
  }, []);

  const handleAdd = async () => {
    if (!newPhone || !newName) return;
    setIsSaving(true);
    try {
      await whatsappApi.createStaffPhone({
        phone: newPhone,
        display_name: newName,
        role: newRole,
      });
      setNewPhone('');
      setNewName('');
      setNewRole('asistente');
      setIsAdding(false);
      toast.success('Telefono registrado');
      loadPhones();
    } catch (err) {
      console.error('Error creating staff phone:', err);
      toast.error('Error al registrar telefono');
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdate = async (id: string) => {
    setIsSaving(true);
    try {
      await whatsappApi.updateStaffPhone(id, {
        display_name: editName,
        role: editRole,
      });
      setEditingId(null);
      toast.success('Telefono actualizado');
      loadPhones();
    } catch (err) {
      console.error('Error updating staff phone:', err);
      toast.error('Error al actualizar telefono');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleActive = async (phone: WAStaffPhone) => {
    try {
      await whatsappApi.updateStaffPhone(phone.id, {
        is_active: !phone.is_active,
      });
      toast.success(phone.is_active ? 'Telefono desactivado' : 'Telefono activado');
      loadPhones();
    } catch (err) {
      console.error('Error toggling staff phone:', err);
      toast.error('Error al cambiar estado');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Eliminar este telefono de staff?')) return;
    try {
      await whatsappApi.deleteStaffPhone(id);
      toast.success('Telefono eliminado');
      loadPhones();
    } catch (err) {
      console.error('Error deleting staff phone:', err);
      toast.error('Error al eliminar telefono');
    }
  };

  const startEdit = (phone: WAStaffPhone) => {
    setEditingId(phone.id);
    setEditName(phone.display_name);
    setEditRole(phone.role);
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Phone className="w-5 h-5 text-green-600" />
          <h3 className="font-semibold text-lg">Telefonos de Staff</h3>
        </div>
        <Button size="sm" onClick={() => setIsAdding(!isAdding)} className="gap-1">
          <Plus className="w-4 h-4" />
          Agregar
        </Button>
      </div>

      {isAdding && (
        <div className="flex gap-2 mb-4 p-3 bg-neutral-50 rounded-lg">
          <Input
            placeholder="Telefono (ej: 521234567890)"
            value={newPhone}
            onChange={(e) => setNewPhone(e.target.value)}
            className="w-48"
          />
          <Input
            placeholder="Nombre"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="w-40"
          />
          <Select value={newRole} onValueChange={(v) => setNewRole(v as StaffRole)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ROLES.map((r) => (
                <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button size="sm" onClick={handleAdd} disabled={isSaving}>
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
            <TableHead>Telefono</TableHead>
            <TableHead>Nombre</TableHead>
            <TableHead>Rol</TableHead>
            <TableHead>Activo</TableHead>
            <TableHead className="w-24">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-8 text-neutral-500">
                Cargando...
              </TableCell>
            </TableRow>
          ) : phones.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-8 text-neutral-500">
                No hay telefonos de staff registrados
              </TableCell>
            </TableRow>
          ) : (
            phones.map((phone) => (
              <TableRow key={phone.id}>
                <TableCell className="font-mono text-sm">{phone.phone}</TableCell>
                <TableCell>
                  {editingId === phone.id ? (
                    <Input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="h-8 w-40"
                    />
                  ) : (
                    phone.display_name
                  )}
                </TableCell>
                <TableCell>
                  {editingId === phone.id ? (
                    <Select value={editRole} onValueChange={(v) => setEditRole(v as StaffRole)}>
                      <SelectTrigger className="h-8 w-28">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {ROLES.map((r) => (
                          <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge variant="secondary">
                      {ROLES.find((r) => r.value === phone.role)?.label || phone.role}
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <Switch
                    checked={phone.is_active}
                    onCheckedChange={() => handleToggleActive(phone)}
                  />
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    {editingId === phone.id ? (
                      <>
                        <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => handleUpdate(phone.id)} disabled={isSaving}>
                          <Check className="w-4 h-4 text-green-600" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => setEditingId(null)}>
                          <X className="w-4 h-4" />
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => startEdit(phone)}>
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => handleDelete(phone.id)}>
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Card>
  );
}
