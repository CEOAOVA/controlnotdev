# ControlNot v2 - Guía de Pruebas con Postman

## 🎯 Objetivo
Validar la migración de `documents.py` a SessionManager y repositorios PostgreSQL.

## 📋 Prerrequisitos

### 1. Configurar Variables de Entorno
Crear archivo `.env` en `backend/`:

```env
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key

# OpenAI (para extracción)
OPENAI_API_KEY=sk-...

# Google Cloud (para OCR)
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# SMTP (para envío de emails)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=tu-email@gmail.com

# Local Storage
LOCAL_STORAGE_PATH=./storage
```

### 2. Instalar Dependencias
```bash
cd backend
pip install -r requirements.txt
```

### 3. Iniciar el Servidor
```bash
uvicorn app.main:app --reload --port 8000
```

El servidor debería iniciar en: `http://localhost:8000`

---

## 🧪 Tests Postman - Flujo Completo

### Test 1: Health Check
**Verificar que el servidor está funcionando**

```
GET http://localhost:8000/api/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-01-23T10:00:00Z"
}
```

---

### Test 2: Crear Cliente
**Endpoint:** `POST /api/clients`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <tu-jwt-token>
```

**Body:**
```json
{
  "tipo_persona": "fisica",
  "nombre_completo": "Juan Carlos Martinez Lopez",
  "rfc": "MALJ850315ABC",
  "curp": "MALJ850315HDFPRN08",
  "email": "juan.martinez@example.com",
  "telefono": "5551234567",
  "direccion": "Av. Insurgentes Sur 1234, Col. Del Valle",
  "ciudad": "Ciudad de México",
  "estado": "CDMX",
  "codigo_postal": "03100"
}
```

**Respuesta esperada:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "...",
  "tipo_persona": "fisica",
  "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ",
  "rfc": "MALJ850315ABC",
  ...
}
```

**Guardar `client_id` para siguiente test**

---

### Test 3: Crear Caso
**Endpoint:** `POST /api/cases`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <tu-jwt-token>
```

**Body:**
```json
{
  "client_id": "<client_id del test anterior>",
  "case_number": "EXP-TEST-2025-001",
  "document_type": "compraventa",
  "description": "Compraventa de inmueble en Polanco",
  "parties": [
    {
      "role": "vendedor",
      "client_id": "<client_id>",
      "nombre": "JUAN CARLOS MARTINEZ LOPEZ"
    },
    {
      "role": "comprador",
      "nombre": "MARIA FERNANDA LOPEZ GARCIA"
    }
  ],
  "metadata": {
    "notas": "Caso de prueba migración v2"
  }
}
```

**Respuesta esperada:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "case_number": "EXP-TEST-2025-001",
  "document_type": "compraventa",
  "status": "draft",
  "client": {
    "nombre_completo": "JUAN CARLOS MARTINEZ LOPEZ",
    ...
  },
  ...
}
```

**Guardar `case_id` para siguiente test**

---

### Test 4: Obtener Categorías de Documento
**Endpoint:** `GET /api/documents/categories?document_type=compraventa`

**Respuesta esperada:**
```json
{
  "parte_a": "Vendedor",
  "parte_b": "Comprador",
  "otros": "Inmueble",
  "document_type": "compraventa"
}
```

---

### Test 5: Subir Template (Primero necesitas este)
**Endpoint:** `POST /api/templates/upload`

**Headers:**
```
Content-Type: multipart/form-data
```

**Body (form-data):**
```
document_type: compraventa
file: <seleccionar archivo .docx>
```

**Respuesta esperada:**
```json
{
  "template_id": "tpl_abc123def456",
  "filename": "template_compraventa.docx",
  "placeholders_found": 25,
  "placeholders": ["NOMBRE_VENDEDOR", "RFC_VENDEDOR", ...],
  ...
}
```

**Guardar `template_id` para siguiente test**

---

### Test 6: Upload Documentos Categorizados ⭐ **MIGRADO**
**Endpoint:** `POST /api/documents/upload`

**Headers:**
```
Content-Type: multipart/form-data
```

**Body (form-data):**
```
document_type: compraventa
template_id: <template_id del test anterior>
parte_a: <archivo PDF vendedor>
parte_b: <archivo PDF comprador>
otros: <archivo PDF inmueble>
```

**Respuesta esperada:**
```json
{
  "session_id": "session_abc123",
  "files_received": {
    "parte_a": 1,
    "parte_b": 1,
    "otros": 1
  },
  "total_files": 3,
  "files": [
    {
      "filename": "ine_vendedor.pdf",
      "size_bytes": 245678,
      "content_type": "application/pdf",
      "category": "parte_a"
    },
    ...
  ],
  "message": "3 archivos recibidos, listos para procesar"
}
```

**Guardar `session_id` para siguiente test**

**✅ Verificación:**
- Documentos se guardan en `SessionManager` (cache temporal)
- No hay error de import circular
- TODO: Verificar que se guardan en `uploaded_files` table

---

### Test 7: Generar Documento ⭐ **MIGRADO**
**Endpoint:** `POST /api/documents/generate`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "template_id": "<template_id>",
  "output_filename": "compraventa_polanco_2025",
  "placeholders": ["NOMBRE_VENDEDOR", "RFC_VENDEDOR", "NOMBRE_COMPRADOR"],
  "responses": {
    "NOMBRE_VENDEDOR": "Juan Carlos Martinez Lopez",
    "RFC_VENDEDOR": "MALJ850315ABC",
    "NOMBRE_COMPRADOR": "Maria Fernanda Lopez Garcia"
  }
}
```

**Respuesta esperada:**
```json
{
  "success": true,
  "document_id": "doc_xyz789abc",
  "filename": "compraventa_polanco_2025.docx",
  "download_url": "/api/documents/download/doc_xyz789abc",
  "size_bytes": 125678,
  "stats": {
    "placeholders_replaced": 3,
    "placeholders_missing": 0,
    "missing_list": [],
    "replaced_in_body": 3,
    "replaced_in_tables": 0,
    "replaced_in_headers": 0,
    "replaced_in_footers": 0,
    "bold_conversions": 0
  },
  "message": "Documento generado: 3 placeholders reemplazados"
}
```

**Guardar `document_id` para siguiente test**

**✅ Verificación:**
- **NO hay import circular** de `templates._template_sessions`
- Usa `SessionManager.get_template_session()` ✅
- Documento se guarda en `SessionManager`
- TODO: Guardar en `documentos` table

---

### Test 8: Descargar Documento ⭐ **MIGRADO**
**Endpoint:** `GET /api/documents/download/<document_id>`

**Ejemplo:**
```
GET http://localhost:8000/api/documents/download/doc_xyz789abc
```

**Respuesta esperada:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Content-Disposition: `attachment; filename=compraventa_polanco_2025.docx`
- Body: Archivo .docx binario

**✅ Verificación:**
- Recupera desde `SessionManager.get_generated_document()`
- Archivo descarga correctamente
- TODO: Si no está en cache, recuperar de DB + Storage

---

### Test 9: Enviar Documento por Email ⭐ **MIGRADO**
**Endpoint:** `POST /api/documents/send-email`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "to_email": "cliente@example.com",
  "subject": "Documento Compraventa - Polanco 2025",
  "body": "Estimado cliente, adjunto encontrará el documento de compraventa.",
  "document_id": "<document_id>",
  "html": false
}
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Email enviado exitosamente a cliente@example.com",
  "to_email": "cliente@example.com",
  "document_filename": "compraventa_polanco_2025.docx"
}
```

**✅ Verificación:**
- Recupera documento desde `SessionManager`
- Email se envía con adjunto
- No hay errores de import circular

---

## 🔍 Verificaciones Críticas

### 1. **No Hay Dependencias Circulares**
```bash
# Buscar imports circulares (no debería aparecer nada)
grep -r "from app.api.endpoints.templates import _template_sessions" backend/app/
```

**Resultado esperado:** No matches found ✅

### 2. **SessionManager Funciona**
```bash
# Verificar que SessionManager se importa correctamente
grep -r "from app.services import.*SessionManager" backend/app/api/endpoints/documents.py
```

**Resultado esperado:** Import encontrado ✅

### 3. **Logs Estructurados**
Al ejecutar los tests, verificar en consola:
```
INFO session_manager_initialized
INFO template_session_stored template_id=tpl_abc123
INFO document_session_stored session_id=session_abc123
INFO Documento generado y guardado en SessionManager doc_id=doc_xyz789
```

---

## 📊 Estadísticas de SessionManager

### Endpoint de Diagnóstico (Agregar temporalmente)
```python
# En documents.py, agregar endpoint temporal:

@router.get("/debug/session-stats")
async def get_session_stats(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Obtener estadísticas del SessionManager (solo desarrollo)"""
    return session_manager.get_stats()
```

**Llamar:**
```
GET http://localhost:8000/api/documents/debug/session-stats
```

**Respuesta esperada:**
```json
{
  "template_sessions": 1,
  "document_sessions": 1,
  "extraction_results": 0,
  "cancelacion_sessions": 0,
  "generated_documents": 1,
  "total_sessions": 3
}
```

---

## 🐛 Troubleshooting

### Error: "Template no encontrado en sesión"
**Causa:** El template_id no está en SessionManager
**Solución:** Primero ejecutar Test 5 (Upload Template) antes de generar documento

### Error: "Documento no encontrado en sesión"
**Causa:** El document_id no existe o expiró
**Solución:**
- Verificar que se ejecutó Test 7 (Generate) antes
- Por defecto, TTL es 48 horas para documentos generados

### Error: "ImportError: cannot import name '_template_sessions'"
**Causa:** Código antiguo todavía tiene import circular
**Solución:** Verificar que `documents.py` usa `SessionManager.get_template_session()`

---

## ✅ Checklist de Migración Completa

- [x] **Imports actualizados** - Sin dependencias circulares
- [x] **SessionManager integrado** - Todos los endpoints usan SessionManager
- [x] **Endpoint /upload migrado** - Usa `store_document_session()`
- [x] **Endpoint /generate migrado** - Usa `get_template_session()` y `store_generated_document()`
- [x] **Endpoint /download migrado** - Usa `get_generated_document()`
- [x] **Endpoint /send-email migrado** - Usa `get_generated_document()`
- [x] **requirements.txt actualizado** - Agregado `supabase==2.3.0`
- [ ] **Tests Postman ejecutados** - Todos los endpoints funcionan
- [ ] **Integración con DB** - Guardar en `documentos` table (TODO)
- [ ] **Integración con Storage** - Subir archivos a Supabase Storage (TODO)

---

## 🚀 Siguientes Pasos (Fase 2)

1. **Integrar con `session_repository`**
   - Guardar sesiones en `sessions` table
   - Persistir datos entre reinicios

2. **Integrar con `uploaded_file_repository`**
   - Guardar metadata de archivos en `uploaded_files` table
   - Trackear archivos por session

3. **Integrar con `document_repository`**
   - Guardar documentos generados en `documentos` table
   - Link con casos y sesiones

4. **Migrar otros endpoints**
   - `extraction.py` - Eliminar `_extraction_results`
   - `templates.py` - Eliminar `_template_sessions`
   - `cancelaciones.py` - Eliminar `_cancelacion_sessions`

---

## 📝 Notas de Desarrollo

### Beneficios de la Migración
- ✅ **Sin dependencias circulares** - Arquitectura limpia
- ✅ **Thread-safe** - SessionManager usa Lock
- ✅ **TTL automático** - Sesiones expiran después de 24h
- ✅ **Cleanup automático** - Libera memoria periódicamente
- ✅ **Estadísticas** - Monitoreo de sesiones activas

### Limitaciones Actuales
- ⚠️ **Solo en memoria** - Se pierde al reiniciar servidor
- ⚠️ **No distribuido** - No funciona con múltiples instancias
- ⚠️ **Sin persistencia** - No se guarda en DB todavía

### Soluciones Futuras
- 🔄 Integrar Redis para cache distribuido
- 💾 Guardar sesiones en PostgreSQL via repositories
- ☁️ Subir archivos a Supabase Storage
- 📊 Integrar con audit_logs table

---

**Versión:** 2.0.0
**Fecha:** 2025-01-23
**Estado:** ✅ Migración Fase 1 Completa
