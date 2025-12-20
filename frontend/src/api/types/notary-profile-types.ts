/**
 * Types for Notary Profile API
 * Used for pre-filling instrument data in extraction
 */

export interface NotaryProfileResponse {
  // Notary identification
  nombre: string;
  rfc: string;
  numero_notaria: number | null;
  numero_notaria_palabras: string | null;
  estado: string;
  ciudad: string | null;
  direccion: string | null;

  // Notary titular data
  notario_nombre: string | null;
  notario_titulo: string;

  // Instrument numbering control
  ultimo_numero_instrumento: number;

  // Computed fields for templates
  notario_completo: string | null;
  lugar_instrumento: string | null;
}

export interface NotaryProfileUpdate {
  notario_nombre?: string;
  notario_titulo?: string;
  numero_notaria?: number;
  numero_notaria_palabras?: string;
  ciudad?: string;
  estado?: string;
  direccion?: string;
}

export interface IncrementInstrumentResponse {
  nuevo_numero: number;
  numero_palabras: string;
}
