/**
 * Models API types
 * Match backend schemas from: backend/app/api/endpoints/models.py
 */

import { DocumentType } from '@/types';

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  supports_json: boolean;
  max_tokens: number;
  recommended: boolean;
}

export interface ModelsListResponse {
  models: ModelInfo[];
  total_models: number;
  using_openrouter: boolean;
  default_model: string;
}

export interface DocumentTypeDetail {
  id: DocumentType;
  name: string;
  fields_count: number;
  description: string;
}

export interface DocumentTypesResponse {
  document_types: DocumentTypeDetail[];
  total_types: number;
}
