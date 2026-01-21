/**
 * Template API types
 * Match backend schemas from: backend/app/schemas/template_schemas.py
 */

import { DocumentType } from '@/types';

export interface PlaceholderExtractionResponse {
  template_id: string;
  template_name: string;
  document_type: DocumentType;
  detected_type?: DocumentType;
  confidence_score: number;
  requires_confirmation: boolean;
  placeholders: string[];
  placeholder_mapping: Record<string, string>;
  total_placeholders: number;
}

export interface TemplateConfirmRequest {
  template_id?: string;
  template_name?: string;
  document_type: DocumentType;
  confirmed?: boolean;
}

export interface TemplateConfirmResponse {
  message: string;
  template_id: string;
  document_type?: DocumentType;
  ready_for_documents: boolean;
}

export interface TemplateInfo {
  id: string;
  name: string;
  display_name?: string;
  size?: number;
  modified?: string;
  source: 'drive' | 'local' | 'uploaded';
  document_type?: DocumentType;
  placeholders?: string[];
  createdAt?: string;
}

export interface TemplateListResponse {
  templates: TemplateInfo[];
  total_count: number;
  sources: Record<string, number>;
}

export interface DocumentTypeInfo {
  id: DocumentType;
  name: string;
  description: string;
}

export interface DocumentTypesListResponse {
  types: DocumentTypeInfo[];
  total: number;
}

// ============================================================
// PLACEHOLDER MAPPING TYPES
// ============================================================

export interface StandardKey {
  key: string;
  description: string;
  aliases: string[];
}

export interface StandardKeysResponse {
  template_id: string;
  template_name: string;
  document_type: DocumentType;
  keys: StandardKey[];
  total: number;
}

export interface TemplateMappingResponse {
  template_id: string;
  template_name: string;
  document_type: DocumentType;
  placeholders: string[];
  mapping: Record<string, string>;
  total_placeholders: number;
  total_mapped: number;
}

export interface UpdateMappingResponse {
  template_id: string;
  template_name: string;
  mapping: Record<string, string>;
  updated: boolean;
  message: string;
}
