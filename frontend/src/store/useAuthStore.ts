/**
 * Auth Store - Manages authentication state and user session
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { supabase } from '@/lib/supabase';
import type { User, Session } from '@supabase/supabase-js';
import { env } from '@/config/env';

// Tipos para eventos de auth
type AuthEventType = 'login_success' | 'login_failed' | 'logout' | 'signup' | 'password_reset';

interface AuthEventPayload {
  event_type: AuthEventType;
  user_id?: string;
  email?: string;
  tenant_id?: string;
  error_message?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Envía evento de autenticación al backend para logging
 * No bloquea ni lanza errores - es fire-and-forget
 */
async function logAuthEvent(payload: AuthEventPayload): Promise<void> {
  try {
    await fetch(`${env.apiUrl}/api/auth/log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    // Silenciar errores de logging - no debe afectar la UX
    console.debug('Auth logging failed (non-critical):', error);
  }
}

interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  tenant_id: string;
  tenant_name?: string;
  notary_number?: string;
}

interface AuthState {
  // Auth state
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updatePassword: (newPassword: string) => Promise<void>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;

  // Session management
  setSession: (session: Session | null) => void;
  setUser: (user: User | null) => void;
  setProfile: (profile: UserProfile | null) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;

  // Helpers
  checkSession: () => Promise<void>;
  refreshSession: () => Promise<void>;
  fetchProfile: (userId: string) => Promise<void>;
  createProfile: (userId: string, email: string, fullName: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        profile: null,
        session: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        // Sign in with email and password
        signIn: async (email: string, password: string) => {
          try {
            set({ isLoading: true, error: null });

            const { data, error } = await supabase.auth.signInWithPassword({
              email,
              password,
            });

            if (error) {
              // Log login fallido
              logAuthEvent({
                event_type: 'login_failed',
                email,
                error_message: error.message,
              });
              throw error;
            }

            if (data.session && data.user) {
              set({
                session: data.session,
                user: data.user,
                isAuthenticated: true,
              });

              // Fetch user profile
              await get().fetchProfile(data.user.id);

              // Log login exitoso (después de obtener el profile para tener tenant_id)
              const profile = get().profile;
              logAuthEvent({
                event_type: 'login_success',
                user_id: data.user.id,
                email: data.user.email,
                tenant_id: profile?.tenant_id,
              });
            }
          } catch (error: any) {
            set({ error: error.message || 'Error al iniciar sesión' });
            throw error;
          } finally {
            set({ isLoading: false });
          }
        },

        // Sign up new user
        signUp: async (email: string, password: string, fullName: string) => {
          try {
            set({ isLoading: true, error: null });

            const { data, error } = await supabase.auth.signUp({
              email,
              password,
              options: {
                data: {
                  full_name: fullName,
                },
              },
            });

            if (error) throw error;

            if (data.session && data.user) {
              set({
                session: data.session,
                user: data.user,
                isAuthenticated: true,
              });

              // Create user profile in database
              await get().createProfile(data.user.id, email, fullName);

              // Log signup exitoso
              const profile = get().profile;
              logAuthEvent({
                event_type: 'signup',
                user_id: data.user.id,
                email: data.user.email,
                tenant_id: profile?.tenant_id,
                metadata: { full_name: fullName },
              });
            }
          } catch (error: any) {
            set({ error: error.message || 'Error al registrar usuario' });
            throw error;
          } finally {
            set({ isLoading: false });
          }
        },

        // Sign out
        signOut: async () => {
          try {
            set({ isLoading: true, error: null });

            // Guardar datos antes de limpiar para el log
            const { user, profile } = get();

            const { error } = await supabase.auth.signOut();
            if (error) throw error;

            // Log logout antes de limpiar el estado
            if (user) {
              logAuthEvent({
                event_type: 'logout',
                user_id: user.id,
                email: user.email ?? undefined,
                tenant_id: profile?.tenant_id,
              });
            }

            set({
              user: null,
              profile: null,
              session: null,
              isAuthenticated: false,
            });
          } catch (error: any) {
            set({ error: error.message || 'Error al cerrar sesión' });
            throw error;
          } finally {
            set({ isLoading: false });
          }
        },

        // Reset password
        resetPassword: async (email: string) => {
          try {
            set({ isLoading: true, error: null });

            const { error } = await supabase.auth.resetPasswordForEmail(email, {
              redirectTo: `${window.location.origin}/reset-password`,
            });

            if (error) throw error;

            // Log solicitud de reset exitosa
            logAuthEvent({
              event_type: 'password_reset',
              email,
            });
          } catch (error: any) {
            set({ error: error.message || 'Error al enviar email de recuperación' });
            throw error;
          } finally {
            set({ isLoading: false });
          }
        },

        // Update password
        updatePassword: async (newPassword: string) => {
          try {
            set({ isLoading: true, error: null });

            const { error } = await supabase.auth.updateUser({
              password: newPassword,
            });

            if (error) throw error;
          } catch (error: any) {
            set({ error: error.message || 'Error al actualizar contraseña' });
            throw error;
          } finally {
            set({ isLoading: false });
          }
        },

        // Update user profile
        updateProfile: async (updates: Partial<UserProfile>) => {
          try {
            set({ isLoading: true, error: null });

            const { user, profile } = get();
            if (!user || !profile) throw new Error('No user logged in');

            const { error } = await supabase
              .from('users')
              .update(updates)
              .eq('id', user.id);

            if (error) throw error;

            set({
              profile: { ...profile, ...updates },
            });
          } catch (error: any) {
            set({ error: error.message || 'Error al actualizar perfil' });
            throw error;
          } finally {
            set({ isLoading: false });
          }
        },

        // Fetch user profile from database
        fetchProfile: async (userId: string) => {
          try {
            const { data, error } = await supabase
              .from('users')
              .select('*, tenants(nombre, numero_notaria)')
              .eq('id', userId)
              .single();

            if (error) throw error;

            if (data) {
              set({
                profile: {
                  id: data.id,
                  email: data.email,
                  full_name: data.nombre_completo,
                  avatar_url: null, // Campo no existe en BD
                  tenant_id: data.tenant_id,
                  tenant_name: data.tenants?.nombre,
                  notary_number: data.tenants?.numero_notaria?.toString(),
                },
              });
            }
          } catch (error: any) {
            console.error('Error fetching profile:', error);
            set({ error: error.message });
          }
        },

        // Create user profile in database
        createProfile: async (userId: string, email: string, fullName: string) => {
          try {
            // TODO: Get or create tenant_id
            const tenantId = 'default-tenant'; // Replace with actual tenant creation logic

            const { error } = await supabase.from('users').insert({
              id: userId,
              email,
              nombre_completo: fullName,
              tenant_id: tenantId,
            });

            if (error) throw error;

            await get().fetchProfile(userId);
          } catch (error: any) {
            console.error('Error creating profile:', error);
            throw error;
          }
        },

        // Session management
        setSession: (session) => set({ session, isAuthenticated: !!session }),
        setUser: (user) => set({ user }),
        setProfile: (profile) => set({ profile }),
        setError: (error) => set({ error }),
        setLoading: (isLoading) => set({ isLoading }),

        // Check current session
        checkSession: async () => {
          try {
            set({ isLoading: true });

            const { data, error } = await supabase.auth.getSession();
            if (error) throw error;

            if (data.session) {
              set({
                session: data.session,
                user: data.session.user,
                isAuthenticated: true,
              });

              await get().fetchProfile(data.session.user.id);
            } else {
              set({
                session: null,
                user: null,
                profile: null,
                isAuthenticated: false,
              });
            }
          } catch (error: any) {
            console.error('Error checking session:', error);
            set({
              session: null,
              user: null,
              profile: null,
              isAuthenticated: false,
            });
          } finally {
            set({ isLoading: false });
          }
        },

        // Refresh session
        refreshSession: async () => {
          try {
            const { data, error } = await supabase.auth.refreshSession();
            if (error) throw error;

            if (data.session) {
              set({
                session: data.session,
                user: data.session.user,
              });
            }
          } catch (error: any) {
            console.error('Error refreshing session:', error);
          }
        },
      }),
      {
        name: 'auth-storage',
        // Only persist necessary auth data
        partialize: (state) => ({
          session: state.session,
          user: state.user,
          profile: state.profile,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AuthStore' }
  )
);

// Flags para evitar loops infinitos
let isFetchingProfile = false;
let profileFetchAttempted = false; // Solo intentar UNA VEZ

// Setup auth state listener
supabase.auth.onAuthStateChange((event, session) => {
  const { setSession, setUser, setLoading } = useAuthStore.getState();

  if (event === 'SIGNED_IN' && session) {
    setSession(session);
    setUser(session.user);
    // NO llamar fetchProfile aquí - signIn() ya lo hace
    // Reset flag porque es nuevo login
    profileFetchAttempted = false;
  }

  if (event === 'SIGNED_OUT') {
    setSession(null);
    setUser(null);
    useAuthStore.getState().setProfile(null);
    // Reset flags
    isFetchingProfile = false;
    profileFetchAttempted = false;
  }

  if (event === 'TOKEN_REFRESHED' && session) {
    setSession(session);
  }

  // Solo hacer fetch en INITIAL_SESSION (cuando se recarga la página con sesión existente)
  // Y solo si NO hemos intentado antes (para evitar loops en caso de error)
  if (event === 'INITIAL_SESSION' && session?.user) {
    const currentProfile = useAuthStore.getState().profile;
    if (!currentProfile && !isFetchingProfile && !profileFetchAttempted) {
      isFetchingProfile = true;
      profileFetchAttempted = true; // Marcar que ya intentamos
      setLoading(true);
      useAuthStore.getState().fetchProfile(session.user.id)
        .catch((err) => {
          console.error('Failed to fetch profile on init:', err);
          // No reintentar - el usuario puede refrescar la página
        })
        .finally(() => {
          isFetchingProfile = false;
          setLoading(false);
        });
    } else if (currentProfile) {
      // Ya tenemos profile, asegurarnos de que isAuthenticated sea true
      setLoading(false);
    }
  }
});
