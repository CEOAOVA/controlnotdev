/**
 * Supabase Client Configuration
 * Singleton instance for authentication and database access
 */

import { createClient } from '@supabase/supabase-js';

// Environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Validate required environment variables (warning only, don't block build)
if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    '[Supabase] Missing environment variables. VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are required.'
  );
}

// Create Supabase client (conditional to allow build without real values)
export const supabase = supabaseUrl && supabaseAnonKey
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        storage: typeof window !== 'undefined' ? window.localStorage : undefined,
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
      },
    })
  : (null as unknown as ReturnType<typeof createClient>);

// Database types (reflect actual Supabase schema)
export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          tenant_id: string;
          email: string;
          nombre_completo: string | null;
          rol: 'admin' | 'notario' | 'asistente';
          activo: boolean;
          metadata: Record<string, unknown>;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['users']['Insert']>;
      };
      tenants: {
        Row: {
          id: string;
          nombre: string;
          rfc: string;
          numero_notaria: number | null;
          estado: string;
          ciudad: string | null;
          activo: boolean;
          metadata: Record<string, unknown>;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['tenants']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['tenants']['Insert']>;
      };
    };
  };
};
