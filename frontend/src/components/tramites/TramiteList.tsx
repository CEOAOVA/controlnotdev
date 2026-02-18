import { useState } from 'react';
import { Plus, Check, Pencil, Trash2, ListTodo } from 'lucide-react';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { TramiteSemaforoPill } from './TramiteSemaforoPill';
import { TramiteForm } from './TramiteForm';
import type { Tramite, TramiteCreateRequest } from '@/api/types/cases-types';

interface TramiteListProps {
  tramites: Tramite[];
  onAdd: (data: TramiteCreateRequest) => Promise<void>;
  onUpdate: (tramiteId: string, data: Record<string, any>) => Promise<void>;
  onComplete: (tramiteId: string) => Promise<void>;
  onRemove: (tramiteId: string) => Promise<void>;
}

export function TramiteList({ tramites, onAdd, onUpdate, onComplete, onRemove }: TramiteListProps) {
  const [showForm, setShowForm] = useState(false);
  const [editingTramite, setEditingTramite] = useState<Tramite | null>(null);

  const handleSubmit = async (data: TramiteCreateRequest) => {
    if (editingTramite) {
      await onUpdate(editingTramite.id, data);
      setEditingTramite(null);
    } else {
      await onAdd(data);
    }
    setShowForm(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-neutral-900">Tramites ({tramites.length})</h3>
        <Button size="sm" className="gap-1" onClick={() => { setEditingTramite(null); setShowForm(true); }}>
          <Plus className="w-4 h-4" />
          Nuevo Tramite
        </Button>
      </div>

      {tramites.length === 0 ? (
        <Card className="p-8">
          <div className="text-center space-y-2">
            <ListTodo className="w-10 h-10 text-neutral-400 mx-auto" />
            <p className="text-neutral-600">No hay tramites registrados</p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="divide-y divide-neutral-200">
            {tramites.map((tramite) => (
              <div key={tramite.id} className="p-4 hover:bg-neutral-50">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    {tramite.semaforo && (
                      <TramiteSemaforoPill semaforo={tramite.semaforo} className="mt-1" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-neutral-900">{tramite.nombre}</p>
                      <p className="text-sm text-neutral-600 capitalize">{tramite.tipo}</p>
                      <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                        {tramite.fecha_limite && (
                          <span>Limite: {format(new Date(tramite.fecha_limite), 'dd/MM/yyyy')}</span>
                        )}
                        {tramite.costo != null && (
                          <span>${tramite.costo.toLocaleString()}</span>
                        )}
                        {tramite.fecha_completado && (
                          <span className="text-green-600">Completado: {format(new Date(tramite.fecha_completado), 'dd/MM/yyyy')}</span>
                        )}
                      </div>
                      {tramite.resultado && (
                        <p className="text-xs text-neutral-500 mt-1">Resultado: {tramite.resultado}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {!tramite.fecha_completado && (
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-green-600" onClick={() => onComplete(tramite.id)} title="Completar">
                        <Check className="w-4 h-4" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => { setEditingTramite(tramite); setShowForm(true); }}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-red-600" onClick={() => onRemove(tramite.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <TramiteForm
        open={showForm}
        onOpenChange={setShowForm}
        onSubmit={handleSubmit}
        initialData={editingTramite || undefined}
      />
    </div>
  );
}
