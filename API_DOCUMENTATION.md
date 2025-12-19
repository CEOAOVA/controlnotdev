# ControlNot v2 - API Documentation

**Version:** 2.0.0
**Base URL:** `http://localhost:8000` (development) | `https://api.your-domain.com` (production)
**Last Updated:** 2025-01-16

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Health Endpoints](#health-endpoints)
3. [Document Types & Models](#document-types--models)
4. [Templates](#templates)
5. [Categories](#categories)
6. [Documents](#documents)
7. [Extraction (OCR & AI)](#extraction-ocr--ai)
8. [Email](#email)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## 1. Authentication

**Status:** Not implemented yet (MVP uses no auth)
**Future:** Will use Bearer tokens or API keys

For current MVP, all endpoints are open. In production, add authentication headers:
```http
Authorization: Bearer YOUR_API_KEY
```

---

## 2. Health Endpoints

### 2.1 Basic Health Check

**Endpoint:** `GET /api/health`

**Description:** Returns basic health status of the application

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-01-16T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is down

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

### 2.2 Services Health Check

**Endpoint:** `GET /api/health/services`

**Description:** Returns detailed health status of all integrated services

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "ai": {
      "status": "healthy",
      "provider": "openrouter",
      "model": "openai/gpt-4o",
      "latency_ms": 150
    },
    "ocr": {
      "status": "healthy",
      "provider": "google_vision",
      "latency_ms": 80
    },
    "email": {
      "status": "healthy",
      "smtp_server": "smtp.gmail.com",
      "latency_ms": 45
    }
  },
  "timestamp": "2025-01-16T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - All services healthy
- `207 Multi-Status` - Some services degraded
- `503 Service Unavailable` - Critical services down

---

## 3. Document Types & Models

### 3.1 List Document Types

**Endpoint:** `GET /api/models/types`

**Description:** Returns all supported document types with metadata

**Response:**
```json
{
  "document_types": [
    {
      "id": "compraventa",
      "name": "Escritura de Compraventa",
      "description": "Compra-venta de bienes inmuebles",
      "total_fields": 47,
      "categories": ["Parte Vendedora", "Parte Compradora", "Inmueble"]
    },
    {
      "id": "donacion",
      "name": "Escritura de Donación",
      "description": "Donación de bienes",
      "total_fields": 49,
      "categories": ["Parte Donadora", "Parte Donataria", "Bien Donado"]
    },
    // ... more types
  ],
  "total": 5
}
```

**Status Codes:**
- `200 OK` - Success

**Example:**
```bash
curl http://localhost:8000/api/models/types
```

---

### 3.2 Get Available AI Models

**Endpoint:** `GET /api/models`

**Description:** Returns list of available AI models for extraction

**Response:**
```json
{
  "models": [
    {
      "id": "openai/gpt-4o",
      "name": "GPT-4 Optimized",
      "provider": "openai",
      "cost_per_1k_tokens": 0.005,
      "speed": "fast"
    },
    {
      "id": "anthropic/claude-3.5-sonnet",
      "name": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "cost_per_1k_tokens": 0.003,
      "speed": "medium"
    },
    // ... more models
  ],
  "default": "openai/gpt-4o"
}
```

**Status Codes:**
- `200 OK` - Success

---

## 4. Templates

### 4.1 List Templates

**Endpoint:** `GET /api/templates/list`

**Query Parameters:**
- `source` (optional): `"local"` or `"drive"` (default: `"local"`)

**Description:** Returns available Word templates

**Response:**
```json
{
  "templates": [
    {
      "id": "tpl_abc123",
      "name": "Compraventa_Template_v2.docx",
      "document_type": "compraventa",
      "placeholders_count": 47,
      "source": "local",
      "size_bytes": 45678,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 3,
  "source": "local"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - No templates found

**Example:**
```bash
curl "http://localhost:8000/api/templates/list?source=local"
```

---

### 4.2 Upload Template

**Endpoint:** `POST /api/templates/upload`

**Content-Type:** `multipart/form-data`

**Request Body:**
- `file` (required): Word document (.docx)
- `document_type` (optional): Type hint (compraventa, donacion, etc.)

**Response:**
```json
{
  "template_id": "tpl_xyz789",
  "filename": "Custom_Compraventa.docx",
  "placeholders": [
    "Parte_Vendedora_Nombre_Completo",
    "RFC_Parte_Vendedora",
    // ... all placeholders
  ],
  "placeholders_count": 42,
  "detected_type": "compraventa",
  "message": "Template uploaded successfully"
}
```

**Status Codes:**
- `201 Created` - Template uploaded
- `400 Bad Request` - Invalid file format
- `413 Payload Too Large` - File too large (> 10MB)

**Example:**
```bash
curl -X POST http://localhost:8000/api/templates/upload \
  -F "file=@/path/to/template.docx" \
  -F "document_type=compraventa"
```

---

### 4.3 Get Template Placeholders

**Endpoint:** `GET /api/templates/{template_id}/placeholders`

**Description:** Extract placeholders from a template

**Response:**
```json
{
  "template_id": "tpl_abc123",
  "placeholders": [
    "Parte_Vendedora_Nombre_Completo",
    "RFC_Parte_Vendedora",
    "CURP_Parte_Vendedora"
  ],
  "total": 47
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Template not found

---

## 5. Categories

### 5.1 Get Categories by Document Type

**Endpoint:** `GET /api/documents/categories`

**Query Parameters:**
- `document_type` (required): Type of document (compraventa, donacion, etc.)

**Description:** Returns the 3 categories for uploading documents

**Response:**
```json
{
  "parte_a": {
    "nombre": "Documentos del Vendedor",
    "icono": "📤",
    "descripcion": "Documentos de identificación y propiedad del vendedor",
    "documentos": [
      "INE/IFE del Vendedor",
      "Acta de Nacimiento",
      "CURP",
      "RFC/Constancia SAT"
    ]
  },
  "parte_b": {
    "nombre": "Documentos del Comprador",
    "icono": "📥",
    "descripcion": "Documentos de identificación del comprador",
    "documentos": [
      "INE/IFE del Comprador",
      "Acta de Nacimiento",
      "CURP",
      "RFC/Constancia SAT"
    ]
  },
  "otros": {
    "nombre": "Documentos del Inmueble",
    "icono": "📋",
    "descripcion": "Documentación legal del inmueble",
    "documentos": [
      "Escritura Antecedente",
      "Certificado Catastral",
      "Certificado de Libertad de Gravamen"
    ]
  },
  "document_type": "compraventa"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid document type
- `404 Not Found` - Document type not found

**Example:**
```bash
curl "http://localhost:8000/api/documents/categories?document_type=compraventa"
```

---

## 6. Documents

### 6.1 Upload Categorized Documents

**Endpoint:** `POST /api/documents/upload`

**Content-Type:** `multipart/form-data`

**Request Body:**
- `document_type` (required): Type of document
- `template_id` (required): Template ID to use
- `parte_a[]` (optional): Files for category A
- `parte_b[]` (optional): Files for category B
- `otros[]` (optional): Files for category C

**Response:**
```json
{
  "session_id": "session_xyz789",
  "files_received": {
    "parte_a": 3,
    "parte_b": 2,
    "otros": 4
  },
  "total_files": 9,
  "files": [
    {
      "filename": "INE_vendedor.jpg",
      "size_bytes": 234567,
      "content_type": "image/jpeg",
      "category": "parte_a"
    }
    // ... more files
  ],
  "message": "9 archivos recibidos, listos para procesar"
}
```

**Status Codes:**
- `200 OK` - Files uploaded
- `400 Bad Request` - No files provided or invalid type
- `413 Payload Too Large` - Files too large

**Example:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "document_type=compraventa" \
  -F "template_id=tpl_abc123" \
  -F "parte_a[]=@INE_vendedor.jpg" \
  -F "parte_a[]=@CURP_vendedor.pdf" \
  -F "parte_b[]=@INE_comprador.jpg"
```

---

### 6.2 Generate Document

**Endpoint:** `POST /api/documents/generate`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "template_id": "tpl_abc123",
  "responses": {
    "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
    "RFC_Parte_Vendedora": "CEAR640813JJ8",
    "Edad_Parte_Vendedora": "sesenta años"
  },
  "placeholders": [
    "Parte_Vendedora_Nombre_Completo",
    "RFC_Parte_Vendedora",
    "Edad_Parte_Vendedora"
  ],
  "output_filename": "Compraventa_Lote_145"
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc_789abc",
  "filename": "Compraventa_Lote_145.docx",
  "download_url": "/api/documents/download/doc_789abc",
  "size_bytes": 45678,
  "stats": {
    "placeholders_replaced": 47,
    "placeholders_missing": 3,
    "missing_list": ["Escritura_Antecedente_Fecha"],
    "replaced_in_body": 30,
    "replaced_in_tables": 15,
    "replaced_in_headers": 1,
    "replaced_in_footers": 1,
    "bold_conversions": 12
  },
  "message": "Documento generado: 47 placeholders reemplazados"
}
```

**Status Codes:**
- `200 OK` - Document generated
- `404 Not Found` - Template not found
- `400 Bad Request` - Invalid request

**Example:**
```bash
curl -X POST http://localhost:8000/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{"template_id":"tpl_abc123","responses":{...},"placeholders":[...],"output_filename":"Doc1"}'
```

---

### 6.3 Download Document

**Endpoint:** `GET /api/documents/download/{doc_id}`

**Description:** Download a generated Word document

**Response:** Binary file (application/vnd.openxmlformats-officedocument.wordprocessingml.document)

**Status Codes:**
- `200 OK` - File download
- `404 Not Found` - Document not found

**Example:**
```bash
curl http://localhost:8000/api/documents/download/doc_789abc \
  -o document.docx
```

---

## 7. Extraction (OCR & AI)

### 7.1 Process OCR

**Endpoint:** `POST /api/extraction/ocr`

**Content-Type:** `multipart/form-data`

**Request Body:**
- `document_type` (required): Type of document
- `Parte A[]` (optional): Images for category A
- `Parte B[]` (optional): Images for category B
- `Otros[]` (optional): Images for category C

**Description:** Performs OCR on uploaded images (parallel processing, 5-10x faster than legacy)

**Response:**
```json
{
  "ocr_results": [
    {
      "category": "Parte A",
      "filename": "INE_vendedor.jpg",
      "text": "RAUL CERVANTES AREVALO\nRFC: CEAR640813JJ8\nCURP: CEAR640813HMNRRL02...",
      "confidence": 0.95,
      "processing_time_ms": 850
    }
    // ... more results
  ],
  "total_images": 9,
  "total_processing_time_ms": 6850,
  "average_confidence": 0.92
}
```

**Status Codes:**
- `200 OK` - OCR completed
- `400 Bad Request` - No images provided
- `500 Internal Server Error` - OCR service error

**Example:**
```bash
curl -X POST http://localhost:8000/api/extraction/ocr \
  -F "document_type=compraventa" \
  -F "Parte A[]=@INE_vendedor.jpg" \
  -F "Parte B[]=@INE_comprador.jpg"
```

---

### 7.2 Extract with AI

**Endpoint:** `POST /api/extraction/ai`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "document_type": "compraventa",
  "ocr_results": [
    {
      "category": "Parte A",
      "filename": "INE_vendedor.jpg",
      "text": "RAUL CERVANTES AREVALO..."
    }
  ],
  "model": "openai/gpt-4o"
}
```

**Response:**
```json
{
  "extracted_data": {
    "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
    "RFC_Parte_Vendedora": "CEAR640813JJ8",
    "CURP_Parte_Vendedora": "CEAR640813HMNRRL02",
    "Edad_Parte_Vendedora": "sesenta años"
    // ... all 47 fields
  },
  "confidence": 0.88,
  "fields_extracted": 42,
  "fields_missing": 5,
  "processing_time_ms": 8500,
  "model_used": "openai/gpt-4o",
  "tokens_used": 1250
}
```

**Status Codes:**
- `200 OK` - Extraction completed
- `400 Bad Request` - Invalid request
- `500 Internal Server Error` - AI service error

**Example:**
```bash
curl -X POST http://localhost:8000/api/extraction/ai \
  -H "Content-Type: application/json" \
  -d '{"document_type":"compraventa","ocr_results":[...]}'
```

---

### 7.3 Save Edited Data

**Endpoint:** `POST /api/extraction/save`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "session_id": "session_xyz789",
  "document_type": "compraventa",
  "edited_data": {
    "Parte_Vendedora_Nombre_Completo": "RAUL CERVANTES AREVALO",
    "RFC_Parte_Vendedora": "CEAR640813JJ8"
    // ... all edited fields
  }
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_xyz789",
  "fields_saved": 47,
  "message": "Datos guardados exitosamente"
}
```

**Status Codes:**
- `200 OK` - Data saved
- `400 Bad Request` - Invalid data
- `404 Not Found` - Session not found

---

### 7.4 Extract with Vision (Claude Vision API)

**Endpoint:** `POST /api/extraction/vision`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "session_id": "session_abc123",
  "document_type": "ine_ife"
}
```

**Description:** Extracts data directly from images using Claude Vision API - no OCR step required. Handles any image orientation automatically.

**Supported Document Types:**
- `ine_ife` - Mexican voter ID (INE/IFE)
- `pasaporte` - Mexican passport
- `curp_constancia` - CURP certificate from RENAPO
- Plus all standard notarial document types

**Response:**
```json
{
  "session_id": "session_abc123",
  "extracted_data": {
    "nombre_completo": "CERVANTES AREVALO RAUL",
    "curp": "CEAR640813HMNRRL02",
    "clave_elector": "CRVRAL64081314H100",
    "fecha_nacimiento": "13/08/1964",
    "sexo": "H",
    "domicilio": "AV HIDALGO 123 COL CENTRO GUADALAJARA JALISCO 44100",
    "seccion_electoral": "1234",
    "estado": "JALISCO",
    "vigencia": "2029"
  },
  "images_processed": 2,
  "total_keys": 13,
  "keys_found": 10,
  "completeness_percent": 76.9,
  "model_used": "claude-sonnet-4-20250514",
  "tokens_used": 3500,
  "processing_time_seconds": 4.2,
  "cache_hit": false
}
```

**Advantages over OCR:**
- **No OCR step required** - Direct image-to-data extraction
- **Handles any orientation** - Horizontal, vertical, rotated images work automatically
- **Higher accuracy** - ~97% vs ~85% with traditional OCR
- **Document type detection** - Visually identifies document type
- **Prompt caching** - ~80% cost savings on repeated requests

**Status Codes:**
- `200 OK` - Extraction completed
- `400 Bad Request` - No images in session
- `404 Not Found` - Session not found
- `500 Internal Server Error` - Vision API error

**Example:**
```bash
curl -X POST http://localhost:8000/api/extraction/vision \
  -H "Content-Type: application/json" \
  -d '{"session_id":"session_abc123","document_type":"ine_ife"}'
```

**Notes:**
- Maximum 20 images per request (Anthropic limit)
- Images are automatically resized if > 1568px
- Images are compressed if > 5MB
- Works best with clear, well-lit photos

---

## 8. Email

### 8.1 Send Document via Email

**Endpoint:** `POST /api/documents/send-email`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "to_email": "cliente@example.com",
  "subject": "Escritura de Compraventa - Lote 145",
  "body": "Estimado cliente,\n\nAdjunto encontrará su escritura de compraventa.\n\nSaludos cordiales.",
  "document_id": "doc_789abc",
  "html": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email enviado exitosamente a cliente@example.com",
  "to_email": "cliente@example.com",
  "document_filename": "Compraventa_Lote_145.docx"
}
```

**Status Codes:**
- `200 OK` - Email sent
- `400 Bad Request` - Invalid email address
- `404 Not Found` - Document not found
- `500 Internal Server Error` - Email service error

**Example:**
```bash
curl -X POST http://localhost:8000/api/documents/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "cliente@example.com",
    "subject": "Su escritura",
    "body": "Adjunto su documento",
    "document_id": "doc_789abc"
  }'
```

---

## 9. Error Handling

All API errors follow this structure:

```json
{
  "detail": "Error message description",
  "error_type": "ValidationError",
  "status_code": 400
}
```

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `400` | Bad Request | Invalid input, missing required fields |
| `401` | Unauthorized | Invalid or missing API key (future) |
| `404` | Not Found | Resource doesn't exist |
| `413` | Payload Too Large | File size exceeds limit |
| `422` | Unprocessable Entity | Validation error in request body |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |
| `503` | Service Unavailable | Service temporarily down |

---

## 10. Rate Limiting

**Status:** Not implemented yet (MVP)

**Future Implementation:**
- **Limit:** 100 requests per minute per IP
- **Headers:**
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1642348800
  ```

---

## 11. Interactive API Documentation

**Swagger UI:** http://localhost:8000/docs

Access interactive API documentation with:
- Try-it-out functionality
- Request/response examples
- Schema definitions
- Authentication testing (future)

**ReDoc:** http://localhost:8000/redoc

Alternative documentation interface with:
- Clean, modern UI
- Searchable endpoints
- Detailed schema information

---

## 12. SDK & Client Libraries

**Status:** Not available yet

**Planned:**
- JavaScript/TypeScript client
- Python client
- CLI tool

---

## 📞 Support

For API support:
- **Issues:** GitHub Issues
- **Documentation:** [Full Documentation](README.md)
- **Email:** support@yourcompany.com

---

**Version:** 2.0.0
**Last Updated:** 2025-01-16
**Maintainer:** ControlNot Team
