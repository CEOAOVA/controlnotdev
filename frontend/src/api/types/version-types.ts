/**
 * Template Version API Types
 * Types for template versioning system
 */

export interface TemplateVersion {
  id: string;
  template_id: string;
  version_number: number;
  storage_path: string;
  placeholders: string[];
  placeholder_mapping: Record<string, string>;
  es_activa: boolean;
  created_at: string;
  created_by?: string;
  notas?: string;
}

export interface TemplateVersionListResponse {
  template_id: string;
  template_name: string;
  versions: TemplateVersion[];
  total_versions: number;
  active_version?: number;
}

export interface VersionCompareRequest {
  version_id_1: string;
  version_id_2: string;
}

export interface VersionCompareResponse {
  version_1: {
    id: string;
    version_number: number;
    placeholders: string[];
  };
  version_2: {
    id: string;
    version_number: number;
    placeholders: string[];
  };
  added_placeholders: string[];
  removed_placeholders: string[];
  unchanged_placeholders: string[];
  total_changes: number;
}

export interface ActivateVersionResponse {
  success: boolean;
  message: string;
  activated_version: TemplateVersion;
  previous_active_version?: number;
}
