/**
 * SecurityTab Component
 * Security settings and password change
 */

import { useState } from 'react';
import { Lock, Eye, EyeOff, Shield, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks';

export function SecurityTab() {
  const toast = useToast();

  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: '',
  });
  const [passwordError, setPasswordError] = useState('');

  const validatePassword = (password: string): boolean => {
    if (password.length < 8) {
      setPasswordError('La contraseña debe tener al menos 8 caracteres');
      return false;
    }
    if (!/[A-Z]/.test(password)) {
      setPasswordError('La contraseña debe contener al menos una mayúscula');
      return false;
    }
    if (!/[a-z]/.test(password)) {
      setPasswordError('La contraseña debe contener al menos una minúscula');
      return false;
    }
    if (!/[0-9]/.test(password)) {
      setPasswordError('La contraseña debe contener al menos un número');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const handleChangePassword = async () => {
    // Validations
    if (!passwords.current || !passwords.new || !passwords.confirm) {
      toast.error('Por favor completa todos los campos');
      return;
    }

    if (passwords.new !== passwords.confirm) {
      toast.error('Las contraseñas nuevas no coinciden');
      return;
    }

    if (!validatePassword(passwords.new)) {
      return;
    }

    try {
      setIsSaving(true);
      // TODO: Implement password change API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      toast.success('Contraseña actualizada exitosamente');
      setPasswords({ current: '', new: '', confirm: '' });
      setIsChangingPassword(false);
    } catch (err: any) {
      toast.error(`Error al cambiar contraseña: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setPasswords({ current: '', new: '', confirm: '' });
    setPasswordError('');
    setIsChangingPassword(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-neutral-900">Seguridad</h2>
        <p className="text-sm text-neutral-600 mt-1">
          Administra tu contraseña y configuración de seguridad
        </p>
      </div>

      {/* Change Password Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Lock className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-medium text-neutral-900">Cambiar Contraseña</h3>
              <p className="text-sm text-neutral-600">
                Actualiza tu contraseña periódicamente para mayor seguridad
              </p>
            </div>
          </div>
          {!isChangingPassword && (
            <Button variant="outline" onClick={() => setIsChangingPassword(true)}>
              Cambiar
            </Button>
          )}
        </div>

        {isChangingPassword && (
          <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-6 space-y-4">
            {/* Current Password */}
            <div>
              <Label htmlFor="current-password">Contraseña Actual</Label>
              <div className="relative mt-2">
                <Input
                  id="current-password"
                  type={showPasswords.current ? 'text' : 'password'}
                  value={passwords.current}
                  onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                  placeholder="Ingresa tu contraseña actual"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswords({ ...showPasswords, current: !showPasswords.current })
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                >
                  {showPasswords.current ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div>
              <Label htmlFor="new-password">Nueva Contraseña</Label>
              <div className="relative mt-2">
                <Input
                  id="new-password"
                  type={showPasswords.new ? 'text' : 'password'}
                  value={passwords.new}
                  onChange={(e) => {
                    setPasswords({ ...passwords, new: e.target.value });
                    if (e.target.value) validatePassword(e.target.value);
                  }}
                  placeholder="Ingresa tu nueva contraseña"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswords({ ...showPasswords, new: !showPasswords.new })
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                >
                  {showPasswords.new ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <Label htmlFor="confirm-password">Confirmar Nueva Contraseña</Label>
              <div className="relative mt-2">
                <Input
                  id="confirm-password"
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={passwords.confirm}
                  onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                  placeholder="Confirma tu nueva contraseña"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                >
                  {showPasswords.confirm ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Password Requirements */}
            {passwordError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{passwordError}</AlertDescription>
              </Alert>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-medium text-blue-900 mb-2">
                Requisitos de contraseña:
              </p>
              <ul className="text-xs text-blue-800 space-y-1">
                <li className="flex items-center gap-2">
                  <span className={passwords.new.length >= 8 ? 'text-green-600' : ''}>
                    • Mínimo 8 caracteres
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <span className={/[A-Z]/.test(passwords.new) ? 'text-green-600' : ''}>
                    • Al menos una mayúscula
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <span className={/[a-z]/.test(passwords.new) ? 'text-green-600' : ''}>
                    • Al menos una minúscula
                  </span>
                </li>
                <li className="flex items-center gap-2">
                  <span className={/[0-9]/.test(passwords.new) ? 'text-green-600' : ''}>
                    • Al menos un número
                  </span>
                </li>
              </ul>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3 pt-2">
              <Button onClick={handleChangePassword} disabled={isSaving} className="gap-2">
                {isSaving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Cambiando...
                  </>
                ) : (
                  <>
                    <Shield className="w-4 h-4" />
                    Cambiar Contraseña
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                Cancelar
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Two-Factor Authentication (Future) */}
      <div className="border-t border-neutral-200 pt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-neutral-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-neutral-600" />
            </div>
            <div>
              <h3 className="font-medium text-neutral-900">
                Autenticación de Dos Factores (2FA)
              </h3>
              <p className="text-sm text-neutral-600">
                Agrega una capa adicional de seguridad a tu cuenta
              </p>
            </div>
          </div>
          <Button variant="outline" disabled>
            Próximamente
          </Button>
        </div>
      </div>
    </div>
  );
}
