/**
 * Application constants
 */

export const DOCUMENT_TYPES = {
  COMPRAVENTA: 'compraventa',
  DONACION: 'donacion',
  TESTAMENTO: 'testamento',
  PODER: 'poder',
  SOCIEDAD: 'sociedad',
} as const;

export const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  compraventa: 'Compraventa',
  donacion: 'Donación',
  testamento: 'Testamento',
  poder: 'Poder',
  sociedad: 'Sociedad',
};

export const CATEGORIES = {
  PARTE_A: 'parte_a',
  PARTE_B: 'parte_b',
  OTROS: 'otros',
} as const;

export const CATEGORY_LABELS: Record<string, string> = {
  parte_a: 'Parte A',
  parte_b: 'Parte B',
  otros: 'Otros',
};

export const WORKFLOW_STEPS = {
  TEMPLATE_SELECTION: 1,
  DOCUMENT_UPLOAD: 2,
  OCR_PROCESSING: 3,
  AI_EXTRACTION: 4,
  DATA_REVIEW: 5,
  GENERATION: 6,
} as const;

export const STEP_LABELS: Record<number, string> = {
  1: 'Selección de Template',
  2: 'Carga de Documentos',
  3: 'Procesamiento OCR',
  4: 'Extracción con IA',
  5: 'Revisión de Datos',
  6: 'Generación',
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ACCEPTED_FILE_TYPES = {
  template: ['.docx'],
  documents: ['.pdf', '.jpg', '.jpeg', '.png'],
};

export const API_TIMEOUT = 120000; // 2 minutes for long operations
