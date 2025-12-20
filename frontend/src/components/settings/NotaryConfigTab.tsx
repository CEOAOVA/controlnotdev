/**
 * NotaryConfigTab Component
 * Notary office configuration with API integration
 *
 * Fields for instrument pre-filling:
 * - notario_nombre: Notary titular name
 * - notario_titulo: Title (Licenciado, Doctor, etc.)
 * - numero_notaria: Notary number
 * - ciudad, estado: Location for lugar_instrumento
 * - ultimo_numero_instrumento: Last instrument number
 */

import { useState, useEffect } from 'react';
import { Save, X, MapPin, User, Hash, RefreshCw, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks';
import { notaryProfileApi } from '@/api/endpoints';
import type { NotaryProfileResponse, NotaryProfileUpdate } from '@/api/types';

const NOTARY_TITLES = [
  'Licenciado',
  'Licenciada',
  'Doctor',
  'Doctora',
  'Maestro',
  'Maestra',
  'Ingeniero',
  'Ingeniera',
];

export function NotaryConfigTab() {
  const toast = useToast();

  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [profile, setProfile] = useState<NotaryProfileResponse | null>(null);

  const [formData, setFormData] = useState<NotaryProfileUpdate>({
    notario_nombre: '',
    notario_titulo: 'Licenciado',
    numero_notaria: undefined,
    numero_notaria_palabras: '',
    ciudad: '',
    estado: '',
    direccion: '',
  });

  // Load profile on mount
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      const data = await notaryProfileApi.getProfile();
      setProfile(data);
      setFormData({
        notario_nombre: data.notario_nombre || '',
        notario_titulo: data.notario_titulo || 'Licenciado',
        numero_notaria: data.numero_notaria || undefined,
        numero_notaria_palabras: data.numero_notaria_palabras || '',
        ciudad: data.ciudad || '',
        estado: data.estado || '',
        direccion: data.direccion || '',
      });
    } catch (err: any) {
      console.error('Error loading notary profile:', err);
      toast.error('Error al cargar perfil de notaria');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);

      // Only send non-empty values
      const updateData: NotaryProfileUpdate = {};
      if (formData.notario_nombre) updateData.notario_nombre = formData.notario_nombre;
      if (formData.notario_titulo) updateData.notario_titulo = formData.notario_titulo;
      if (formData.numero_notaria) updateData.numero_notaria = formData.numero_notaria;
      if (formData.numero_notaria_palabras) updateData.numero_notaria_palabras = formData.numero_notaria_palabras;
      if (formData.ciudad) updateData.ciudad = formData.ciudad;
      if (formData.estado) updateData.estado = formData.estado;
      if (formData.direccion) updateData.direccion = formData.direccion;

      const updated = await notaryProfileApi.updateProfile(updateData);
      setProfile(updated);

      toast.success('Perfil de notaria actualizado');
      setIsEditing(false);
    } catch (err: any) {
      toast.error(`Error al actualizar: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (profile) {
      setFormData({
        notario_nombre: profile.notario_nombre || '',
        notario_titulo: profile.notario_titulo || 'Licenciado',
        numero_notaria: profile.numero_notaria || undefined,
        numero_notaria_palabras: profile.numero_notaria_palabras || '',
        ciudad: profile.ciudad || '',
        estado: profile.estado || '',
        direccion: profile.direccion || '',
      });
    }
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        <span className="ml-2 text-neutral-600">Cargando perfil...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-neutral-900">
            Configuracion de Notaria
          </h2>
          <p className="text-sm text-neutral-600 mt-1">
            Datos para pre-llenado de instrumentos notariales
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={loadProfile} title="Recargar">
            <RefreshCw className="w-4 h-4" />
          </Button>
          {!isEditing && (
            <Button variant="outline" onClick={() => setIsEditing(true)}>
              Editar
            </Button>
          )}
        </div>
      </div>

      {/* Current Profile Summary */}
      {profile && !isEditing && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-primary-900 mb-2">
            Datos del Instrumento (Auto-llenado)
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-primary-600">Notario:</span>{' '}
              <span className="text-primary-900 font-medium">
                {profile.notario_completo || 'No configurado'}
              </span>
            </div>
            <div>
              <span className="text-primary-600">Notaria No.:</span>{' '}
              <span className="text-primary-900 font-medium">
                {profile.numero_notaria_palabras?.toUpperCase() || profile.numero_notaria || 'No configurado'}
              </span>
            </div>
            <div>
              <span className="text-primary-600">Lugar:</span>{' '}
              <span className="text-primary-900 font-medium">
                {profile.lugar_instrumento || 'No configurado'}
              </span>
            </div>
            <div>
              <span className="text-primary-600">Ultimo instrumento:</span>{' '}
              <span className="text-primary-900 font-medium">
                #{profile.ultimo_numero_instrumento}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Form Fields */}
      <div className="space-y-4">
        {/* Notary Name */}
        <div>
          <Label htmlFor="notary-name" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            Nombre del Notario Titular
          </Label>
          <Input
            id="notary-name"
            type="text"
            value={formData.notario_nombre || ''}
            onChange={(e) =>
              setFormData({ ...formData, notario_nombre: e.target.value })
            }
            disabled={!isEditing}
            placeholder="Patricia Servin Maldonado"
            className="mt-2"
          />
          <p className="text-xs text-neutral-500 mt-1">
            Se usara como "notario_actuante" en los instrumentos
          </p>
        </div>

        {/* Title and Number Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Notary Title */}
          <div>
            <Label htmlFor="notary-title">Titulo</Label>
            <Select
              value={formData.notario_titulo || 'Licenciado'}
              onValueChange={(value) =>
                setFormData({ ...formData, notario_titulo: value })
              }
              disabled={!isEditing}
            >
              <SelectTrigger className="mt-2">
                <SelectValue placeholder="Seleccionar titulo" />
              </SelectTrigger>
              <SelectContent>
                {NOTARY_TITLES.map((title) => (
                  <SelectItem key={title} value={title}>
                    {title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Notary Number */}
          <div>
            <Label htmlFor="notary-number" className="flex items-center gap-2">
              <Hash className="w-4 h-4" />
              Numero de Notaria
            </Label>
            <Input
              id="notary-number"
              type="number"
              value={formData.numero_notaria || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  numero_notaria: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              disabled={!isEditing}
              placeholder="14"
              className="mt-2"
            />
          </div>

          {/* Number in Words */}
          <div>
            <Label htmlFor="notary-number-words">En palabras</Label>
            <Input
              id="notary-number-words"
              type="text"
              value={formData.numero_notaria_palabras || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  numero_notaria_palabras: e.target.value,
                })
              }
              disabled={!isEditing}
              placeholder="catorce"
              className="mt-2"
            />
            <p className="text-xs text-neutral-500 mt-1">
              Se auto-genera si se deja vacio
            </p>
          </div>
        </div>

        {/* Location */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="city" className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              Ciudad
            </Label>
            <Input
              id="city"
              type="text"
              value={formData.ciudad || ''}
              onChange={(e) =>
                setFormData({ ...formData, ciudad: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Celaya"
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="state">Estado</Label>
            <Input
              id="state"
              type="text"
              value={formData.estado || ''}
              onChange={(e) =>
                setFormData({ ...formData, estado: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Guanajuato"
              className="mt-2"
            />
          </div>
        </div>

        {/* Address */}
        <div>
          <Label htmlFor="address">Direccion</Label>
          <Textarea
            id="address"
            value={formData.direccion || ''}
            onChange={(e) =>
              setFormData({ ...formData, direccion: e.target.value })
            }
            disabled={!isEditing}
            placeholder="Calle, Numero, Colonia, C.P."
            className="mt-2"
            rows={2}
          />
        </div>
      </div>

      {/* Actions */}
      {isEditing && (
        <div className="flex items-center gap-3 pt-4 border-t border-neutral-200">
          <Button onClick={handleSave} disabled={isSaving} className="gap-2">
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Guardando...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Guardar Cambios
              </>
            )}
          </Button>
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isSaving}
            className="gap-2"
          >
            <X className="w-4 h-4" />
            Cancelar
          </Button>
        </div>
      )}
    </div>
  );
}
