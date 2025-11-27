# 📚 API Examples - ControlNot v2

Ejemplos completos de cómo usar la API de ControlNot v2 con autenticación.

---

## 🔐 Autenticación

### Login y Obtener Token

```typescript
// Frontend: Login con Supabase
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://tu-proyecto.supabase.co',
  'tu-anon-key'
)

const login = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: 'admin@notaria1.mx',
    password: 'TuPasswordSeguro123!'
  })

  if (error) throw error

  const token = data.session.access_token
  console.log('Token JWT:', token)

  return token
}
```

---

## 📋 Clients API

### Crear Cliente

```bash
# cURL
curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_persona": "fisica",
    "nombre_completo": "Juan Pérez García",
    "rfc": "PEGJ850101ABC",
    "curp": "PEGJ850101HDFRNN09",
    "email": "juan.perez@email.com",
    "telefono": "+52 55 9876 5432",
    "direccion": "Calle Falsa 123",
    "ciudad": "Ciudad de México",
    "estado": "CDMX",
    "codigo_postal": "03100"
  }'
```

```typescript
// TypeScript/JavaScript
const createClient = async (token: string) => {
  const response = await fetch('http://localhost:8000/api/clients', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      tipo_persona: 'fisica',
      nombre_completo: 'Juan Pérez García',
      rfc: 'PEGJ850101ABC',
      email: 'juan.perez@email.com',
      telefono: '+52 55 9876 5432'
    })
  })

  const client = await response.json()
  console.log('Cliente creado:', client)
  return client
}
```

```python
# Python con requests
import requests

def create_client(token: str):
    response = requests.post(
        'http://localhost:8000/api/clients',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'tipo_persona': 'fisica',
            'nombre_completo': 'Juan Pérez García',
            'rfc': 'PEGJ850101ABC',
            'email': 'juan.perez@email.com',
            'telefono': '+52 55 9876 5432'
        }
    )

    client = response.json()
    print(f"Cliente creado: {client['id']}")
    return client
```

### Listar Clientes

```bash
# cURL
curl -X GET "http://localhost:8000/api/clients?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```typescript
// TypeScript
const listClients = async (token: string, page = 1) => {
  const response = await fetch(
    `http://localhost:8000/api/clients?page=${page}&page_size=20`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  )

  const data = await response.json()
  console.log(`Total clientes: ${data.total}`)
  return data.clients
}
```

### Buscar Cliente

```bash
# cURL
curl -X GET "http://localhost:8000/api/clients/search/?q=Juan" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```typescript
// TypeScript
const searchClients = async (token: string, query: string) => {
  const response = await fetch(
    `http://localhost:8000/api/clients/search/?q=${encodeURIComponent(query)}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  )

  const data = await response.json()
  return data.clients
}
```

---

## 📁 Cases API

### Crear Caso

```bash
# cURL
curl -X POST http://localhost:8000/api/cases \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "case_number": "EXP-2025-001",
    "document_type": "compraventa",
    "description": "Compraventa de inmueble en Polanco",
    "parties": [
      {
        "role": "vendedor",
        "nombre": "María González",
        "metadata": {"rfc": "GOGM800101ABC"}
      },
      {
        "role": "comprador",
        "nombre": "Juan Pérez",
        "metadata": {"rfc": "PEGJ850101ABC"}
      }
    ]
  }'
```

```typescript
// TypeScript
interface Party {
  role: string
  nombre: string
  metadata?: Record<string, any>
}

const createCase = async (
  token: string,
  clientId: string,
  caseNumber: string,
  documentType: string,
  parties: Party[]
) => {
  const response = await fetch('http://localhost:8000/api/cases', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      client_id: clientId,
      case_number: caseNumber,
      document_type: documentType,
      description: `Caso de ${documentType}`,
      parties
    })
  })

  const caseData = await response.json()
  console.log('Caso creado:', caseData.id)
  return caseData
}
```

### Obtener Estadísticas de Casos

```bash
# cURL
curl -X GET http://localhost:8000/api/cases/statistics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```typescript
// TypeScript
const getCaseStatistics = async (token: string) => {
  const response = await fetch(
    'http://localhost:8000/api/cases/statistics',
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  )

  const stats = await response.json()
  console.log('Estadísticas:', {
    total_casos: stats.total_cases,
    por_estado: stats.by_status,
    por_tipo: stats.by_document_type
  })

  return stats
}
```

---

## 📄 Documents API

### Subir Documentos Categorizados

```bash
# cURL
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "document_type=compraventa" \
  -F "template_id=template-uuid-here" \
  -F "parte_a=@/path/to/ine_comprador.pdf" \
  -F "parte_a=@/path/to/comprobante_comprador.pdf" \
  -F "parte_b=@/path/to/ine_vendedor.pdf" \
  -F "parte_b=@/path/to/escrituras_vendedor.pdf" \
  -F "otros=@/path/to/avaluo.pdf"
```

```typescript
// TypeScript con FormData
const uploadDocuments = async (
  token: string,
  documentType: string,
  templateId: string,
  files: {
    parteA: File[]
    parteB: File[]
    otros: File[]
  }
) => {
  const formData = new FormData()
  formData.append('document_type', documentType)
  formData.append('template_id', templateId)

  // Agregar archivos de cada categoría
  files.parteA.forEach(file => formData.append('parte_a', file))
  files.parteB.forEach(file => formData.append('parte_b', file))
  files.otros.forEach(file => formData.append('otros', file))

  const response = await fetch('http://localhost:8000/api/documents/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })

  const result = await response.json()
  console.log('Session ID:', result.session_id)
  console.log('Archivos recibidos:', result.files_received)

  return result
}
```

### Generar Documento

```bash
# cURL
curl -X POST http://localhost:8000/api/documents/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "template-uuid-here",
    "output_filename": "Escritura_Compraventa_2025_001",
    "placeholders": [
      "NOMBRE_COMPRADOR",
      "NOMBRE_VENDEDOR",
      "PRECIO_VENTA",
      "DESCRIPCION_INMUEBLE"
    ],
    "responses": {
      "NOMBRE_COMPRADOR": "Juan Pérez García",
      "NOMBRE_VENDEDOR": "María González López",
      "PRECIO_VENTA": "$2,500,000.00 MXN",
      "DESCRIPCION_INMUEBLE": "Casa habitación ubicada en Polanco..."
    }
  }'
```

```typescript
// TypeScript
const generateDocument = async (
  token: string,
  templateId: string,
  filename: string,
  data: Record<string, string>
) => {
  const placeholders = Object.keys(data)

  const response = await fetch('http://localhost:8000/api/documents/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      template_id: templateId,
      output_filename: filename,
      placeholders,
      responses: data
    })
  })

  const result = await response.json()
  console.log('Documento generado:', result.doc_id)
  console.log('Placeholders reemplazados:', result.placeholders_replaced)

  return result
}
```

### Descargar Documento

```bash
# cURL
curl -X GET "http://localhost:8000/api/documents/download/doc-uuid-here" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o documento.docx
```

```typescript
// TypeScript
const downloadDocument = async (token: string, docId: string) => {
  const response = await fetch(
    `http://localhost:8000/api/documents/download/${docId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  )

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)

  // Descargar automáticamente
  const a = document.createElement('a')
  a.href = url
  a.download = `documento_${docId}.docx`
  a.click()

  URL.revokeObjectURL(url)
}
```

---

## 🔍 Extraction API

### Procesar OCR

```bash
# cURL
curl -X POST "http://localhost:8000/api/extraction/ocr?session_id=session-uuid-here" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```typescript
// TypeScript
const processOCR = async (token: string, sessionId: string) => {
  const response = await fetch(
    `http://localhost:8000/api/extraction/ocr?session_id=${sessionId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  )

  const result = await response.json()
  console.log('Texto extraído:', result.extracted_text.substring(0, 200) + '...')
  console.log('Archivos procesados:', result.files_processed)
  console.log('Tiempo de procesamiento:', result.processing_time_seconds, 's')

  return result
}
```

### Extracción con IA

```bash
# cURL
curl -X POST http://localhost:8000/api/extraction/ai \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid-here",
    "text": "Texto extraído del OCR...",
    "document_type": "compraventa",
    "template_placeholders": [
      "NOMBRE_COMPRADOR",
      "NOMBRE_VENDEDOR",
      "PRECIO_VENTA"
    ]
  }'
```

```typescript
// TypeScript
const extractWithAI = async (
  token: string,
  sessionId: string,
  text: string,
  documentType: string,
  placeholders: string[]
) => {
  const response = await fetch('http://localhost:8000/api/extraction/ai', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      text,
      document_type: documentType,
      template_placeholders: placeholders
    })
  })

  const result = await response.json()
  console.log('Datos extraídos:', result.extracted_data)
  console.log('Completitud:', result.completeness_percent, '%')
  console.log('Modelo usado:', result.model_used)
  console.log('Tokens consumidos:', result.tokens_used)

  return result
}
```

### Confirmar Datos Editados

```bash
# cURL
curl -X POST http://localhost:8000/api/extraction/edit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid-here",
    "edited_data": {
      "NOMBRE_COMPRADOR": "Juan Pérez García (Corregido)",
      "PRECIO_VENTA": "$2,500,000.00 MXN"
    },
    "confirmed": true
  }'
```

```typescript
// TypeScript
const confirmEditedData = async (
  token: string,
  sessionId: string,
  editedData: Record<string, string>
) => {
  const response = await fetch('http://localhost:8000/api/extraction/edit', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      edited_data: editedData,
      confirmed: true
    })
  })

  const result = await response.json()
  console.log('Datos confirmados correctamente')
  return result
}
```

---

## 📝 Templates API

### Listar Templates

```bash
# cURL
curl -X GET "http://localhost:8000/api/templates?document_type=compraventa" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```typescript
// TypeScript
const listTemplates = async (
  token: string,
  documentType?: string
) => {
  const url = new URL('http://localhost:8000/api/templates')
  if (documentType) {
    url.searchParams.append('document_type', documentType)
  }

  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  const templates = await response.json()
  console.log(`Templates encontrados: ${templates.length}`)
  return templates
}
```

### Subir Template

```bash
# cURL
curl -X POST http://localhost:8000/api/templates/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "document_type=compraventa" \
  -F "template_name=Compraventa Estándar 2025" \
  -F "file=@/path/to/template.docx"
```

```typescript
// TypeScript
const uploadTemplate = async (
  token: string,
  documentType: string,
  templateName: string,
  file: File
) => {
  const formData = new FormData()
  formData.append('document_type', documentType)
  formData.append('template_name', templateName)
  formData.append('file', file)

  const response = await fetch('http://localhost:8000/api/templates/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })

  const result = await response.json()
  console.log('Template subido:', result.template_id)
  console.log('Placeholders detectados:', result.placeholders)

  return result
}
```

---

## 🔄 Flujo Completo: Compraventa

```typescript
// Ejemplo completo de procesamiento de compraventa

const processCompraventa = async (token: string) => {
  // 1. Crear cliente
  console.log('📝 Paso 1: Crear cliente...')
  const client = await createClient(token)

  // 2. Crear caso
  console.log('📁 Paso 2: Crear caso...')
  const caseData = await createCase(
    token,
    client.id,
    'EXP-2025-001',
    'compraventa',
    [
      { role: 'comprador', nombre: 'Juan Pérez' },
      { role: 'vendedor', nombre: 'María González' }
    ]
  )

  // 3. Subir documentos
  console.log('📤 Paso 3: Subir documentos...')
  const uploadResult = await uploadDocuments(
    token,
    'compraventa',
    'template-uuid',
    {
      parteA: [ineComprador, comprobanteComprador],
      parteB: [ineVendedor, escriturasVendedor],
      otros: [avaluo]
    }
  )

  // 4. Procesar OCR
  console.log('🔍 Paso 4: Procesar OCR...')
  const ocrResult = await processOCR(token, uploadResult.session_id)

  // 5. Extraer con IA
  console.log('🤖 Paso 5: Extraer datos con IA...')
  const extractionResult = await extractWithAI(
    token,
    uploadResult.session_id,
    ocrResult.extracted_text,
    'compraventa',
    ['NOMBRE_COMPRADOR', 'NOMBRE_VENDEDOR', 'PRECIO_VENTA']
  )

  // 6. Usuario revisa y edita datos (simulado)
  console.log('✏️ Paso 6: Confirmar datos...')
  await confirmEditedData(
    token,
    uploadResult.session_id,
    extractionResult.extracted_data
  )

  // 7. Generar documento final
  console.log('📄 Paso 7: Generar documento...')
  const document = await generateDocument(
    token,
    'template-uuid',
    'Escritura_Compraventa_2025_001',
    extractionResult.extracted_data
  )

  // 8. Descargar documento
  console.log('⬇️ Paso 8: Descargar documento...')
  await downloadDocument(token, document.doc_id)

  console.log('✅ Proceso completado exitosamente')
  return document
}
```

---

## ⚙️ Health Check

```bash
# cURL
curl -X GET http://localhost:8000/api/health
```

```typescript
// TypeScript
const checkHealth = async () => {
  const response = await fetch('http://localhost:8000/api/health')
  const health = await response.json()

  console.log('Estado API:', health.status)
  console.log('Base de datos:', health.database)
  console.log('Servicios:', health.services)

  return health
}
```

---

## 📊 Respuestas de Error

### 401 Unauthorized

```json
{
  "success": false,
  "error": "Invalid authentication credentials",
  "error_code": "UNAUTHORIZED",
  "status_code": 401
}
```

### 404 Not Found

```json
{
  "success": false,
  "error": "Cliente no encontrado",
  "error_code": "NOT_FOUND",
  "status_code": 404
}
```

### 422 Validation Error

```json
{
  "success": false,
  "error": "Error de validación",
  "error_code": "VALIDATION_ERROR",
  "status_code": 422,
  "validation_errors": [
    {
      "loc": ["body", "rfc"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🛠️ Tips y Mejores Prácticas

### 1. Manejo de Tokens

```typescript
// Renovar token automáticamente
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    // Actualizar token en tus requests
    updateAuthToken(session.access_token)
  }
})
```

### 2. Retry con Exponential Backoff

```typescript
const fetchWithRetry = async (
  url: string,
  options: RequestInit,
  maxRetries = 3
) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options)
      if (response.ok) return response

      if (response.status === 429) {
        // Rate limited - esperar antes de retry
        await new Promise(resolve => setTimeout(resolve, 2 ** i * 1000))
        continue
      }

      throw new Error(`HTTP ${response.status}`)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, 2 ** i * 1000))
    }
  }
}
```

### 3. Progress Tracking

```typescript
const uploadWithProgress = async (
  token: string,
  file: File,
  onProgress: (percent: number) => void
) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = (e.loaded / e.total) * 100
        onProgress(percent)
      }
    })

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`))
      }
    })

    xhr.open('POST', 'http://localhost:8000/api/documents/upload')
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)

    const formData = new FormData()
    formData.append('parte_a', file)
    xhr.send(formData)
  })
}
```

---

**Última actualización**: 2025-01-23
**Versión**: 2.0.0
**Documentación completa**: [AUTHENTICATION.md](./AUTHENTICATION.md)
