/**
 * ProfileTab Component
 * User profile management
 */

import { useState, useEffect } from 'react';
import { Camera, Save, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth, useToast } from '@/hooks';

export function ProfileTab() {
  const { userName, userEmail } = useAuth();
  const toast = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: userName || '',
    email: userEmail || '',
    phone: '',
    position: '',
  });

  useEffect(() => {
    setFormData({
      name: userName || '',
      email: userEmail || '',
      phone: '',
      position: '',
    });
  }, [userName, userEmail]);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      // TODO: Implement profile update API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast.success('Perfil actualizado exitosamente');
      setIsEditing(false);
    } catch (err: any) {
      toast.error(`Error al actualizar perfil: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: userName || '',
      email: userEmail || '',
      phone: '',
      position: '',
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-neutral-900">Perfil de Usuario</h2>
        <p className="text-sm text-neutral-600 mt-1">
          Administra tu información personal y foto de perfil
        </p>
      </div>

      {/* Profile Photo */}
      <div className="flex items-center gap-6">
        <div className="relative">
          <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-3xl font-semibold text-primary-600">
              {formData.name
                .split(' ')
                .map((n) => n[0])
                .join('')
                .toUpperCase()
                .substring(0, 2)}
            </span>
          </div>
          <button
            className="absolute bottom-0 right-0 w-8 h-8 bg-white border-2 border-neutral-200 rounded-full flex items-center justify-center hover:bg-neutral-50 transition-colors"
            disabled={!isEditing}
          >
            <Camera className="w-4 h-4 text-neutral-600" />
          </button>
        </div>
        <div>
          <h3 className="font-medium text-neutral-900">{formData.name}</h3>
          <p className="text-sm text-neutral-600">{formData.email}</p>
          {!isEditing && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(true)}
              className="mt-2"
            >
              Editar Perfil
            </Button>
          )}
        </div>
      </div>

      {/* Form Fields */}
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Name */}
          <div>
            <Label htmlFor="name">Nombre Completo</Label>
            <Input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              disabled={!isEditing}
              className="mt-2"
            />
          </div>

          {/* Email */}
          <div>
            <Label htmlFor="email">Correo Electrónico</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              disabled={!isEditing}
              className="mt-2"
            />
          </div>

          {/* Phone */}
          <div>
            <Label htmlFor="phone">Teléfono</Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              disabled={!isEditing}
              placeholder="+52 55 1234 5678"
              className="mt-2"
            />
          </div>

          {/* Position */}
          <div>
            <Label htmlFor="position">Cargo</Label>
            <Input
              id="position"
              type="text"
              value={formData.position}
              onChange={(e) => setFormData({ ...formData, position: e.target.value })}
              disabled={!isEditing}
              placeholder="Ej: Notario Titular"
              className="mt-2"
            />
          </div>
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
