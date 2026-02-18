import { useState } from 'react';
import { Plus, Pencil, Trash2, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { PartyForm } from './PartyForm';
import type { CaseParty, PartyCreateRequest } from '@/api/types/cases-types';

interface PartyListProps {
  parties: CaseParty[];
  onAdd: (data: PartyCreateRequest) => Promise<void>;
  onUpdate: (partyId: string, data: Record<string, any>) => Promise<void>;
  onRemove: (partyId: string) => Promise<void>;
}

export function PartyList({ parties, onAdd, onUpdate, onRemove }: PartyListProps) {
  const [showForm, setShowForm] = useState(false);
  const [editingParty, setEditingParty] = useState<CaseParty | null>(null);

  const handleSubmit = async (data: PartyCreateRequest) => {
    if (editingParty) {
      await onUpdate(editingParty.id, data);
      setEditingParty(null);
    } else {
      await onAdd(data);
    }
    setShowForm(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-neutral-900">Partes ({parties.length})</h3>
        <Button size="sm" className="gap-1" onClick={() => { setEditingParty(null); setShowForm(true); }}>
          <Plus className="w-4 h-4" />
          Agregar Parte
        </Button>
      </div>

      {parties.length === 0 ? (
        <Card className="p-8">
          <div className="text-center space-y-2">
            <Users className="w-10 h-10 text-neutral-400 mx-auto" />
            <p className="text-neutral-600">No hay partes registradas</p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 border-b border-neutral-200">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-medium text-neutral-600 uppercase">Rol</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-neutral-600 uppercase">Nombre</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-neutral-600 uppercase">RFC</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-neutral-600 uppercase">Tipo</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-neutral-600 uppercase">Contacto</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-neutral-600 uppercase">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {parties.map((party) => (
                  <tr key={party.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-3 text-sm font-medium capitalize text-neutral-900">{party.role}</td>
                    <td className="px-4 py-3 text-sm text-neutral-700">{party.nombre}</td>
                    <td className="px-4 py-3 text-sm text-neutral-700">{party.rfc || '-'}</td>
                    <td className="px-4 py-3 text-sm capitalize text-neutral-700">{party.tipo_persona || '-'}</td>
                    <td className="px-4 py-3 text-sm text-neutral-700">{party.email || party.telefono || '-'}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => { setEditingParty(party); setShowForm(true); }}>
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-red-600 hover:text-red-700" onClick={() => onRemove(party.id)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile */}
          <div className="md:hidden divide-y divide-neutral-200">
            {parties.map((party) => (
              <div key={party.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-neutral-900">{party.nombre}</p>
                    <p className="text-sm text-neutral-600 capitalize">{party.role}</p>
                    {party.rfc && <p className="text-xs text-neutral-500">RFC: {party.rfc}</p>}
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => { setEditingParty(party); setShowForm(true); }}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-red-600" onClick={() => onRemove(party.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <PartyForm
        open={showForm}
        onOpenChange={setShowForm}
        onSubmit={handleSubmit}
        initialData={editingParty || undefined}
      />
    </div>
  );
}
