/**
 * PreferencesTab Component
 * System preferences and customization
 */

import { useState } from 'react';
import { Save, X, Globe, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks';

export function PreferencesTab() {
  const toast = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    language: 'es',
    timezone: 'America/Mexico_City',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: '24h',
  });

  const handleSave = async () => {
    try {
      setIsSaving(true);
      // TODO: Implement preferences update API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast.success('Preferencias actualizadas');
      setIsEditing(false);
    } catch (err: any) {
      toast.error(`Error al actualizar preferencias: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      language: 'es',
      timezone: 'America/Mexico_City',
      dateFormat: 'DD/MM/YYYY',
      timeFormat: '24h',
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-neutral-900">Preferencias</h2>
          <p className="text-sm text-neutral-600 mt-1">
            Personaliza tu experiencia en el sistema
          </p>
        </div>
        {!isEditing && (
          <Button variant="outline" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
        )}
      </div>

      <div className="space-y-6">
        {/* Language */}
        <div>
          <Label htmlFor="language" className="flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Idioma
          </Label>
          <Select
            value={formData.language}
            onValueChange={(value) => setFormData({ ...formData, language: value })}
            disabled={!isEditing}
          >
            <SelectTrigger className="mt-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="es">Español</SelectItem>
              <SelectItem value="en">English</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-neutral-500 mt-1">
            Idioma de la interfaz y notificaciones
          </p>
        </div>

        {/* Timezone */}
        <div>
          <Label htmlFor="timezone" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Zona Horaria
          </Label>
          <Select
            value={formData.timezone}
            onValueChange={(value) => setFormData({ ...formData, timezone: value })}
            disabled={!isEditing}
          >
            <SelectTrigger className="mt-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="America/Mexico_City">Ciudad de México (GMT-6)</SelectItem>
              <SelectItem value="America/Monterrey">Monterrey (GMT-6)</SelectItem>
              <SelectItem value="America/Tijuana">Tijuana (GMT-8)</SelectItem>
              <SelectItem value="America/Cancun">Cancún (GMT-5)</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-neutral-500 mt-1">
            Zona horaria para fechas y horas en documentos
          </p>
        </div>

        {/* Date Format */}
        <div>
          <Label htmlFor="date-format">Formato de Fecha</Label>
          <Select
            value={formData.dateFormat}
            onValueChange={(value) => setFormData({ ...formData, dateFormat: value })}
            disabled={!isEditing}
          >
            <SelectTrigger className="mt-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="DD/MM/YYYY">DD/MM/YYYY (31/12/2024)</SelectItem>
              <SelectItem value="MM/DD/YYYY">MM/DD/YYYY (12/31/2024)</SelectItem>
              <SelectItem value="YYYY-MM-DD">YYYY-MM-DD (2024-12-31)</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-neutral-500 mt-1">
            Formato para mostrar fechas en el sistema
          </p>
        </div>

        {/* Time Format */}
        <div>
          <Label htmlFor="time-format">Formato de Hora</Label>
          <Select
            value={formData.timeFormat}
            onValueChange={(value) => setFormData({ ...formData, timeFormat: value })}
            disabled={!isEditing}
          >
            <SelectTrigger className="mt-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">24 horas (14:30)</SelectItem>
              <SelectItem value="12h">12 horas (2:30 PM)</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-neutral-500 mt-1">
            Formato para mostrar horas en el sistema
          </p>
        </div>
      </div>

      {/* Actions */}
      {isEditing && (
        <div className="flex items-center gap-3 pt-4 border-t border-neutral-200">
          <Button onClick={handleSave} disabled={isSaving} className="gap-2">
            {isSaving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Guardando...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Guardar Cambios
              </>
            )}
          </Button>
          <Button variant="outline" onClick={handleCancel} disabled={isSaving} className="gap-2">
            <X className="w-4 h-4" />
            Cancelar
          </Button>
        </div>
      )}
    </div>
  );
}
