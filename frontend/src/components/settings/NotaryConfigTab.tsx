/**
 * NotaryConfigTab Component
 * Notary office configuration
 */

import { useState } from 'react';
import { Save, X, MapPin, Phone, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAuth, useToast } from '@/hooks';

export function NotaryConfigTab() {
  const { tenantName } = useAuth();
  const toast = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: tenantName || '',
    notaryNumber: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    phone: '',
    email: '',
    website: '',
  });

  const handleSave = async () => {
    try {
      setIsSaving(true);
      // TODO: Implement notary config update API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast.success('Configuración de notaría actualizada');
      setIsEditing(false);
    } catch (err: any) {
      toast.error(`Error al actualizar configuración: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: tenantName || '',
      notaryNumber: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      phone: '',
      email: '',
      website: '',
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-neutral-900">Configuración de Notaría</h2>
          <p className="text-sm text-neutral-600 mt-1">
            Información oficial de tu notaría
          </p>
        </div>
        {!isEditing && (
          <Button variant="outline" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
        )}
      </div>

      <div className="space-y-4">
        {/* Notary Name */}
        <div>
          <Label htmlFor="notary-name">Nombre de la Notaría</Label>
          <Input
            id="notary-name"
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            disabled={!isEditing}
            placeholder="Notaría Pública No. 123"
            className="mt-2"
          />
        </div>

        {/* Notary Number */}
        <div>
          <Label htmlFor="notary-number">Número de Notaría</Label>
          <Input
            id="notary-number"
            type="text"
            value={formData.notaryNumber}
            onChange={(e) => setFormData({ ...formData, notaryNumber: e.target.value })}
            disabled={!isEditing}
            placeholder="123"
            className="mt-2"
          />
        </div>

        {/* Address */}
        <div>
          <Label htmlFor="address" className="flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            Dirección
          </Label>
          <Textarea
            id="address"
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            disabled={!isEditing}
            placeholder="Calle, Número, Colonia"
            className="mt-2"
            rows={2}
          />
        </div>

        {/* City, State, Zip */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="city">Ciudad</Label>
            <Input
              id="city"
              type="text"
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              disabled={!isEditing}
              placeholder="Ciudad de México"
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="state">Estado</Label>
            <Input
              id="state"
              type="text"
              value={formData.state}
              onChange={(e) => setFormData({ ...formData, state: e.target.value })}
              disabled={!isEditing}
              placeholder="CDMX"
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="zip">Código Postal</Label>
            <Input
              id="zip"
              type="text"
              value={formData.zipCode}
              onChange={(e) => setFormData({ ...formData, zipCode: e.target.value })}
              disabled={!isEditing}
              placeholder="01000"
              className="mt-2"
            />
          </div>
        </div>

        {/* Contact Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="notary-phone" className="flex items-center gap-2">
              <Phone className="w-4 h-4" />
              Teléfono
            </Label>
            <Input
              id="notary-phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              disabled={!isEditing}
              placeholder="+52 55 1234 5678"
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="notary-email" className="flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Email
            </Label>
            <Input
              id="notary-email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              disabled={!isEditing}
              placeholder="contacto@notaria123.mx"
              className="mt-2"
            />
          </div>
        </div>

        {/* Website */}
        <div>
          <Label htmlFor="website">Sitio Web</Label>
          <Input
            id="website"
            type="url"
            value={formData.website}
            onChange={(e) => setFormData({ ...formData, website: e.target.value })}
            disabled={!isEditing}
            placeholder="https://www.notaria123.mx"
            className="mt-2"
          />
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
