/**
 * Login Page
 * Authentication page with sign in and sign up forms
 */

import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Eye, EyeOff, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/hooks';
import { motion, AnimatePresence } from 'framer-motion';

type AuthMode = 'signin' | 'signup' | 'reset';

export function Login() {
  const { signIn, signUp, resetPassword, isAuthenticated, isLoading, error, clearError } = useAuth();

  const [mode, setMode] = useState<AuthMode>('signin');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
    confirmPassword: '',
  });
  const [localError, setLocalError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setLocalError(null);
    clearError();
    setSuccessMessage(null);
  };

  const validateForm = (): boolean => {
    if (!formData.email || !formData.email.includes('@')) {
      setLocalError('Por favor ingresa un email válido');
      return false;
    }

    if (mode === 'signin' || mode === 'signup') {
      if (!formData.password || formData.password.length < 6) {
        setLocalError('La contraseña debe tener al menos 6 caracteres');
        return false;
      }
    }

    if (mode === 'signup') {
      if (!formData.fullName || formData.fullName.length < 2) {
        setLocalError('Por favor ingresa tu nombre completo');
        return false;
      }

      if (formData.password !== formData.confirmPassword) {
        setLocalError('Las contraseñas no coinciden');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      if (mode === 'signin') {
        await signIn(formData.email, formData.password);
      } else if (mode === 'signup') {
        await signUp(formData.email, formData.password, formData.fullName);
        setSuccessMessage('Cuenta creada exitosamente. Revisa tu email para confirmar tu cuenta.');
      } else if (mode === 'reset') {
        await resetPassword(formData.email);
        setSuccessMessage('Email de recuperación enviado. Revisa tu bandeja de entrada.');
      }
    } catch (err: any) {
      // Error is handled by the store
      console.error('Auth error:', err);
    }
  };

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    setLocalError(null);
    clearError();
    setSuccessMessage(null);
    setFormData({
      email: formData.email, // Keep email
      password: '',
      fullName: '',
      confirmPassword: '',
    });
  };

  return (
    <div className="min-h-screen w-full flex bg-white font-sans text-slate-900">
      {/* Left Side - Form Section */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center p-8 lg:p-12 xl:p-24 relative">

        <div className="w-full max-w-sm">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="mb-12"
          >
            <div className="flex items-center gap-3 mb-8">
              <img src="/logo.jpeg" alt="Aurinot Logo" className="h-12 w-auto rounded-lg" />
              <span className="text-xl font-bold tracking-tight text-slate-900">Aurinot</span>
            </div>
            <h1 className="text-3xl lg:text-4xl font-semibold text-slate-900 mb-3 tracking-tight">
              {mode === 'signin' && 'Bienvenido'}
              {mode === 'signup' && 'Crear cuenta'}
              {mode === 'reset' && 'Recuperar'}
            </h1>
            <p className="text-slate-500 text-base">
              {mode === 'signin' && 'Ingresa tus credenciales para continuar.'}
              {mode === 'signup' && 'Comienza a gestionar tu notaría hoy.'}
              {mode === 'reset' && 'Ingresa tu email para restablecer.'}
            </p>
          </motion.div>

          {/* Form */}
          <motion.form
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            onSubmit={handleSubmit}
            className="space-y-5"
          >
            <AnimatePresence mode="wait">
              {/* Email Field */}
              <motion.div
                key="email-field"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1.5"
              >
                <Label htmlFor="email" className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Email</Label>
                <div className="relative group">
                  <Input
                    id="email"
                    type="email"
                    placeholder="nombre@notaria.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="h-11 bg-transparent border-slate-300 focus:border-slate-900 focus:ring-0 rounded-md transition-all duration-300 placeholder:text-slate-400"
                    required
                    disabled={isLoading}
                  />
                </div>
              </motion.div>

              {/* Full Name Field (Sign Up only) */}
              {mode === 'signup' && (
                <motion.div
                  key="fullname-field"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-1.5"
                >
                  <Label htmlFor="fullName" className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Nombre Completo</Label>
                  <div className="relative group">
                    <Input
                      id="fullName"
                      type="text"
                      placeholder="Juan Pérez"
                      value={formData.fullName}
                      onChange={(e) => handleInputChange('fullName', e.target.value)}
                      className="h-11 bg-transparent border-slate-300 focus:border-slate-900 focus:ring-0 rounded-md transition-all duration-300 placeholder:text-slate-400"
                      required
                      disabled={isLoading}
                    />
                  </div>
                </motion.div>
              )}

              {/* Password Field */}
              {(mode === 'signin' || mode === 'signup') && (
                <motion.div
                  key="password-field"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-1.5"
                >
                  <div className="flex justify-between items-center">
                    <Label htmlFor="password" className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Contraseña</Label>
                    {mode === 'signin' && (
                      <button
                        type="button"
                        onClick={() => switchMode('reset')}
                        className="text-xs text-slate-500 hover:text-slate-900 transition-colors"
                      >
                        ¿Olvidaste tu contraseña?
                      </button>
                    )}
                  </div>
                  <div className="relative group">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className="h-11 bg-transparent border-slate-300 focus:border-slate-900 focus:ring-0 rounded-md transition-all duration-300 placeholder:text-slate-400 pr-10"
                      required
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-900 transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Confirm Password Field (Sign Up only) */}
              {mode === 'signup' && (
                <motion.div
                  key="confirm-password-field"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-1.5"
                >
                  <Label htmlFor="confirmPassword" className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Confirmar</Label>
                  <div className="relative group">
                    <Input
                      id="confirmPassword"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      className="h-11 bg-transparent border-slate-300 focus:border-slate-900 focus:ring-0 rounded-md transition-all duration-300 placeholder:text-slate-400"
                      required
                      disabled={isLoading}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Messages */}
            <AnimatePresence>
              {(error || localError) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <p className="text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-100">
                    {error || localError}
                  </p>
                </motion.div>
              )}

              {successMessage && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <p className="text-sm text-emerald-600 bg-emerald-50 p-3 rounded-md border border-emerald-100 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    {successMessage}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full h-11 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-md transition-all duration-300 shadow-none hover:shadow-lg hover:shadow-slate-200"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Procesando...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  {mode === 'signin' && 'Iniciar Sesión'}
                  {mode === 'signup' && 'Crear Cuenta'}
                  {mode === 'reset' && 'Enviar'}
                  <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </Button>

            {/* Mode Switcher */}
            <div className="pt-6 text-center border-t border-slate-100 mt-6">
              {mode === 'signin' && (
                <p className="text-sm text-slate-500">
                  ¿No tienes cuenta?{' '}
                  <button
                    type="button"
                    onClick={() => switchMode('signup')}
                    className="text-slate-900 font-medium hover:underline transition-all"
                  >
                    Regístrate
                  </button>
                </p>
              )}
              {(mode === 'signup' || mode === 'reset') && (
                <p className="text-sm text-slate-500">
                  ¿Ya tienes cuenta?{' '}
                  <button
                    type="button"
                    onClick={() => switchMode('signin')}
                    className="text-slate-900 font-medium hover:underline transition-all"
                  >
                    Inicia sesión
                  </button>
                </p>
              )}
            </div>
          </motion.form>
        </div>

        {/* Footer */}
        <div className="absolute bottom-8 text-slate-300 text-xs">
          © 2024 Aurinot
        </div>
      </div>

      {/* Right Side - Brand Section (High Contrast) */}
      <div className="hidden lg:flex w-1/2 bg-slate-950 relative items-center justify-center p-12 overflow-hidden">
        {/* Subtle Grid Pattern (White opacity) */}
        <div className="absolute inset-0 opacity-[0.05]"
          style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '32px 32px' }}>
        </div>

        <div className="relative z-10 max-w-md">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="space-y-8"
          >
            {/* Logo removed from here */}

            <div className="space-y-4">
              <h2 className="text-3xl font-semibold text-white leading-tight tracking-tight">
                Gestión notarial <br />
                <span className="text-slate-400">simplificada.</span>
              </h2>
              <p className="text-slate-400 text-lg leading-relaxed font-light">
                La plataforma integral para la notaría moderna. Seguridad, eficiencia y control en un solo lugar.
              </p>
            </div>

            <div className="flex items-center gap-4 pt-4">
              <div className="h-px w-12 bg-slate-700"></div>
              <p className="text-sm text-slate-500 font-medium tracking-widest uppercase">Enterprise Edition</p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
