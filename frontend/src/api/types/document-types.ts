/**
 * Document API types
 * Match backend schemas from: backend/app/schemas/document_schemas.py
 */

import { Category, DocumentType } from '@/types';

export interface CategoryInfo {
  id: Category;
  name: string;
  description: string;
  expected_documents: string[];
  icon?: string;
  /** Si la categoría es obligatoria para el tipo de documento (default: true) */
  required?: boolean;
}

export interface CategoriesResponse {
  document_type: DocumentType;
  categories: CategoryInfo[];
  total: number;
}

export interface CategorizedDocumentsUploadResponse {
  session_id: string;
  document_type: DocumentType;
  categorized_files: Record<Category, string[]>;
  total_files: number;
  message: string;
}

export interface DocumentGenerationRequest {
  template_id: string;
  responses: Record<string, string>;
  placeholders: string[];
  output_filename: string;
}

export interface DocumentGenerationStats {
  placeholders_replaced: number;
  placeholders_missing: number;
  missing_list: string[];
  replaced_in_body: number;
  replaced_in_tables: number;
  bold_conversions: number;
}

export interface DocumentGenerationResponse {
  success: boolean;
  document_id: string;
  filename: string;
  download_url: string;
  size_bytes: number;
  stats: DocumentGenerationStats;
  message: string;
}

export interface SendEmailRequest {
  to_email: string;
  subject: string;
  body: string;
  document_id: string;
  html?: boolean;
}

export interface SendEmailResponse {
  success: boolean;
  message: string;
  to_email: string;
  document_filename?: string;
}
