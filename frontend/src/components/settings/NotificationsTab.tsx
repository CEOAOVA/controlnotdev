/**
 * NotificationsTab Component
 * Email and notification preferences
 */

import { useState } from 'react';
import { Save, X, Mail, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks';

interface NotificationSettings {
  emailNotifications: boolean;
  documentGenerated: boolean;
  documentShared: boolean;
  systemUpdates: boolean;
  securityAlerts: boolean;
  weeklyReport: boolean;
  monthlyReport: boolean;
}

export function NotificationsTab() {
  const toast = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState<NotificationSettings>({
    emailNotifications: true,
    documentGenerated: true,
    documentShared: true,
    systemUpdates: false,
    securityAlerts: true,
    weeklyReport: false,
    monthlyReport: true,
  });

  const handleSave = async () => {
    try {
      setIsSaving(true);
      // TODO: Implement notification settings update API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast.success('Preferencias de notificaciones actualizadas');
      setIsEditing(false);
    } catch (err: any) {
      toast.error(`Error al actualizar preferencias: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setSettings({
      emailNotifications: true,
      documentGenerated: true,
      documentShared: true,
      systemUpdates: false,
      securityAlerts: true,
      weeklyReport: false,
      monthlyReport: true,
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-neutral-900">Notificaciones</h2>
          <p className="text-sm text-neutral-600 mt-1">
            Administra cómo y cuándo recibes notificaciones
          </p>
        </div>
        {!isEditing && (
          <Button variant="outline" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
        )}
      </div>

      <div className="space-y-6">
        {/* Master Toggle */}
        <div className="flex items-center justify-between p-4 bg-primary-50 border border-primary-200 rounded-lg">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-primary-600" />
            <div>
              <Label htmlFor="email-notifications" className="font-medium">
                Notificaciones por Email
              </Label>
              <p className="text-xs text-neutral-600">
                Activar/desactivar todas las notificaciones por correo
              </p>
            </div>
          </div>
          <Switch
            id="email-notifications"
            checked={settings.emailNotifications}
            onCheckedChange={(checked) =>
              setSettings({ ...settings, emailNotifications: checked })
            }
            disabled={!isEditing}
          />
        </div>

        {/* Document Notifications */}
        <div>
          <h3 className="font-medium text-neutral-900 mb-4 flex items-center gap-2">
            <Bell className="w-4 h-4" />
            Notificaciones de Documentos
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="doc-generated">Documento Generado</Label>
                <p className="text-xs text-neutral-600">
                  Recibir notificación cuando un documento se genera exitosamente
                </p>
              </div>
              <Switch
                id="doc-generated"
                checked={settings.documentGenerated}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, documentGenerated: checked })
                }
                disabled={!isEditing || !settings.emailNotifications}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="doc-shared">Documento Compartido</Label>
                <p className="text-xs text-neutral-600">
                  Recibir notificación cuando se comparte un documento
                </p>
              </div>
              <Switch
                id="doc-shared"
                checked={settings.documentShared}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, documentShared: checked })
                }
                disabled={!isEditing || !settings.emailNotifications}
              />
            </div>
          </div>
        </div>

        {/* System Notifications */}
        <div className="border-t border-neutral-200 pt-6">
          <h3 className="font-medium text-neutral-900 mb-4">Notificaciones del Sistema</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="system-updates">Actualizaciones del Sistema</Label>
                <p className="text-xs text-neutral-600">
                  Recibir información sobre nuevas funciones y mejoras
                </p>
              </div>
              <Switch
                id="system-updates"
                checked={settings.systemUpdates}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, systemUpdates: checked })
                }
                disabled={!isEditing || !settings.emailNotifications}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="security-alerts">Alertas de Seguridad</Label>
                <p className="text-xs text-neutral-600">
                  Notificaciones importantes sobre la seguridad de tu cuenta
                </p>
              </div>
              <Switch
                id="security-alerts"
                checked={settings.securityAlerts}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, securityAlerts: checked })
                }
                disabled={!isEditing || !settings.emailNotifications}
              />
            </div>
          </div>
        </div>

        {/* Report Notifications */}
        <div className="border-t border-neutral-200 pt-6">
          <h3 className="font-medium text-neutral-900 mb-4">Reportes Periódicos</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="weekly-report">Reporte Semanal</Label>
                <p className="text-xs text-neutral-600">
                  Resumen de actividad semanal todos los lunes
                </p>
              </div>
              <Switch
                id="weekly-report"
                checked={settings.weeklyReport}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, weeklyReport: checked })
                }
                disabled={!isEditing || !settings.emailNotifications}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="monthly-report">Reporte Mensual</Label>
                <p className="text-xs text-neutral-600">
                  Estadísticas mensuales el primer día de cada mes
                </p>
              </div>
              <Switch
                id="monthly-report"
                checked={settings.monthlyReport}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, monthlyReport: checked })
                }
                disabled={!isEditing || !settings.emailNotifications}
              />
            </div>
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
