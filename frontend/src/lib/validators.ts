/**
 * Mexican legal document validators
 * RFC, CURP, dates, and other notarial field formats
 */

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

// ============================
// RFC Validation
// ============================

const RFC_PATTERN = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/;

export function validateRFC(value: string): ValidationResult {
  if (!value) return { valid: true }; // Empty is OK (optional field)

  const normalized = value.toUpperCase().replace(/[\s-]/g, '');

  if (normalized.length !== 12 && normalized.length !== 13) {
    return { valid: false, message: `RFC debe tener 12 o 13 caracteres (tiene ${normalized.length})` };
  }

  if (!RFC_PATTERN.test(normalized)) {
    return { valid: false, message: 'Formato de RFC inválido' };
  }

  // Validate embedded date (positions 4-9 for personas físicas, 3-8 for morales)
  const dateStart = normalized.length === 13 ? 4 : 3;
  const dateStr = normalized.substring(dateStart, dateStart + 6);
  const month = parseInt(dateStr.substring(2, 4));
  const day = parseInt(dateStr.substring(4, 6));

  if (month < 1 || month > 12) {
    return { valid: false, message: `RFC: mes inválido (${month})` };
  }
  if (day < 1 || day > 31) {
    return { valid: false, message: `RFC: día inválido (${day})` };
  }

  return { valid: true };
}

// ============================
// CURP Validation
// ============================

const CURP_PATTERN = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$/;

const ESTADOS_CURP = new Set([
  'AS', 'BC', 'BS', 'CC', 'CL', 'CM', 'CS', 'CH', 'DF', 'DG',
  'GT', 'GR', 'HG', 'JC', 'MC', 'MN', 'MS', 'NT', 'NL', 'OC',
  'PL', 'QT', 'QR', 'SP', 'SL', 'SR', 'TC', 'TS', 'TL', 'VZ',
  'YN', 'ZS', 'NE',
]);

export function validateCURP(value: string): ValidationResult {
  if (!value) return { valid: true };

  const normalized = value.toUpperCase().replace(/\s/g, '');

  if (normalized.length !== 18) {
    return { valid: false, message: `CURP debe tener 18 caracteres (tiene ${normalized.length})` };
  }

  if (!CURP_PATTERN.test(normalized)) {
    return { valid: false, message: 'Formato de CURP inválido' };
  }

  // Validate embedded date
  const month = parseInt(normalized.substring(6, 8));
  const day = parseInt(normalized.substring(8, 10));

  if (month < 1 || month > 12) {
    return { valid: false, message: `CURP: mes inválido (${month})` };
  }
  if (day < 1 || day > 31) {
    return { valid: false, message: `CURP: día inválido (${day})` };
  }

  // Validate state code
  const stateCode = normalized.substring(11, 13);
  if (!ESTADOS_CURP.has(stateCode)) {
    return { valid: false, message: `CURP: código de estado no reconocido (${stateCode})` };
  }

  return { valid: true };
}

// ============================
// Date Validation (DD/MM/YYYY)
// ============================

const DATE_PATTERN = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
const DATE_DASH_PATTERN = /^(\d{1,2})-(\d{1,2})-(\d{4})$/;

export function validateFecha(value: string): ValidationResult {
  if (!value) return { valid: true };

  const trimmed = value.trim();
  const match = DATE_PATTERN.exec(trimmed) || DATE_DASH_PATTERN.exec(trimmed);

  if (!match) {
    return { valid: false, message: 'Formato de fecha inválido (usar DD/MM/AAAA)' };
  }

  const day = parseInt(match[1]);
  const month = parseInt(match[2]);
  const year = parseInt(match[3]);

  if (month < 1 || month > 12) {
    return { valid: false, message: `Mes inválido: ${month}` };
  }
  if (day < 1 || day > 31) {
    return { valid: false, message: `Día inválido: ${day}` };
  }

  // Validate with actual Date object
  const date = new Date(year, month - 1, day);
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) {
    return { valid: false, message: `Fecha no existe: ${trimmed}` };
  }

  if (year < 1900) {
    return { valid: false, message: 'Año demasiado antiguo (mínimo 1900)' };
  }
  if (year > new Date().getFullYear() + 1) {
    return { valid: false, message: 'Año en el futuro' };
  }

  return { valid: true };
}

// ============================
// Código Postal
// ============================

export function validateCodigoPostal(value: string): ValidationResult {
  if (!value) return { valid: true };
  const normalized = value.replace(/\s/g, '');
  if (!/^\d{5}$/.test(normalized)) {
    return { valid: false, message: 'Código postal debe ser de 5 dígitos' };
  }
  return { valid: true };
}

// ============================
// Clave de Elector
// ============================

export function validateClaveElector(value: string): ValidationResult {
  if (!value) return { valid: true };
  const normalized = value.toUpperCase().replace(/\s/g, '');
  if (normalized.length !== 18) {
    return { valid: false, message: `Clave elector debe tener 18 caracteres (tiene ${normalized.length})` };
  }
  if (!/^[A-Z]{6}\d{8}[A-Z0-9]{4}$/.test(normalized)) {
    return { valid: false, message: 'Formato de clave elector inválido' };
  }
  return { valid: true };
}

// ============================
// Auto-detect validator by field name
// ============================

const FIELD_VALIDATOR_MAP: Record<string, (value: string) => ValidationResult> = {};

// RFC fields
for (const key of ['rfc', 'rfc_parte_a', 'rfc_parte_b', 'rfc_donante', 'rfc_donatario', 'rfc_vendedor', 'rfc_comprador']) {
  FIELD_VALIDATOR_MAP[key] = validateRFC;
}

// CURP fields
for (const key of ['curp', 'curp_parte_a', 'curp_parte_b', 'curp_donante', 'curp_donatario', 'curp_vendedor', 'curp_comprador', 'curp_testador', 'curp_poderdante', 'curp_apoderado']) {
  FIELD_VALIDATOR_MAP[key] = validateCURP;
}

// Date fields
for (const key of ['fecha_nacimiento', 'fecha_nacimiento_parte_a', 'fecha_nacimiento_parte_b', 'fecha_escritura', 'fecha_otorgamiento', 'fecha_firma', 'vigencia']) {
  FIELD_VALIDATOR_MAP[key] = validateFecha;
}

// CP fields
for (const key of ['codigo_postal', 'cp', 'cp_predio']) {
  FIELD_VALIDATOR_MAP[key] = validateCodigoPostal;
}

// Clave elector fields
for (const key of ['clave_elector', 'clave_elector_parte_a', 'clave_elector_parte_b']) {
  FIELD_VALIDATOR_MAP[key] = validateClaveElector;
}

/**
 * Get the validator function for a field name, if one exists.
 * Also checks partial matches (e.g. field containing 'curp' → CURP validator).
 */
export function getFieldValidator(fieldName: string): ((value: string) => ValidationResult) | null {
  const lower = fieldName.toLowerCase();

  // Exact match
  if (FIELD_VALIDATOR_MAP[lower]) {
    return FIELD_VALIDATOR_MAP[lower];
  }

  // Partial match
  if (lower.includes('curp')) return validateCURP;
  if (lower.includes('rfc')) return validateRFC;
  if (lower.includes('fecha') || lower.includes('nacimiento')) return validateFecha;
  if (lower.includes('codigo_postal') || lower === 'cp') return validateCodigoPostal;
  if (lower.includes('clave_elector')) return validateClaveElector;

  return null;
}
