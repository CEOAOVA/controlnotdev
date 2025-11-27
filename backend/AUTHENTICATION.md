# 🔐 Autenticación en ControlNot v2

## Descripción General

ControlNot v2 utiliza **Supabase Auth** para autenticación y autorización, con una arquitectura multi-tenant que garantiza aislamiento completo de datos entre notarías.

### Características Clave

- ✅ **JWT Tokens**: Tokens seguros generados por Supabase Auth
- ✅ **Multi-Tenant**: Aislamiento completo por `tenant_id` (notaría)
- ✅ **Row Level Security (RLS)**: Políticas de BD automáticas
- ✅ **Frontend-Managed**: Tokens generados en el frontend
- ✅ **Backend Validation**: Validación de tokens en cada request
- ✅ **Optional Auth**: Compatibilidad con endpoints sin autenticación

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │ 1. Login
         ▼
┌─────────────────┐
│ Supabase Auth   │──► Genera JWT Token
└────────┬────────┘
         │ 2. Token JWT
         ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
└────────┬────────┘
         │ 3. Valida Token
         │ 4. Extrae tenant_id
         ▼
┌─────────────────┐
│   PostgreSQL    │──► RLS aplica filtros
│   (Supabase)    │    automáticamente
└─────────────────┘
```

---

## 📋 Setup Inicial

### Paso 1: Crear Usuario en Supabase

1. Ve al Dashboard de Supabase
2. Navega a **Authentication** > **Users**
3. Click en **"Add user"** > **"Create new user"**
4. Completa:
   - **Email**: `admin@notaria1.mx`
   - **Password**: `TuPasswordSeguro123!`
   - **Auto Confirm User**: ✅ (activar)
5. Anota el **UUID** del usuario creado

### Paso 2: Ejecutar Script de Setup

```sql
-- Editar el archivo setup_auth.sql
-- Reemplazar <USER_UUID> con el UUID del paso 1

-- Ejecutar en Supabase SQL Editor:
\i backend/database/migrations/setup_auth.sql
```

Este script crea:
- ✅ Tenant (notaría) de ejemplo
- ✅ Vinculación usuario → tenant
- ✅ Datos de prueba (cliente, template)
- ✅ Preferencias de estilo

### Paso 3: Obtener Credenciales

```bash
# En el proyecto frontend:
# Crear archivo .env con:

VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu-anon-key-aqui
```

### Paso 4: Implementar Login en Frontend

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// src/hooks/useAuth.ts
export const useAuth = () => {
  const login = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) throw error

    // Token está en data.session.access_token
    return data.session
  }

  const getToken = async () => {
    const { data } = await supabase.auth.getSession()
    return data.session?.access_token
  }

  return { login, getToken }
}
```

---

## 🔑 Uso en el Backend

### Endpoints Protegidos (Requerido)

Para endpoints que **SIEMPRE** requieren autenticación:

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import get_authenticated_user, get_user_tenant_id

router = APIRouter()

@router.post("/clients")
async def create_client(
    data: ClientCreateRequest,
    user: dict = Depends(get_authenticated_user),  # Requerido
    tenant_id: str = Depends(get_user_tenant_id)   # Requerido
):
    """
    Endpoint protegido - requiere autenticación

    Si el token es inválido → 401 Unauthorized
    """
    # user contiene: {id, email, metadata}
    # tenant_id contiene: UUID de la notaría

    client = await client_repository.create_client(
        tenant_id=UUID(tenant_id),
        ...data.dict()
    )
    return client
```

### Endpoints Opcionales (Backward Compatibility)

Para endpoints en **migración gradual**:

```python
from typing import Optional
from fastapi import Depends
from app.core.dependencies import get_optional_tenant_id

@router.post("/documents/upload")
async def upload_documents(
    files: List[UploadFile],
    tenant_id: Optional[str] = Depends(get_optional_tenant_id)  # Opcional
):
    """
    Endpoint híbrido - funciona con y sin autenticación

    Si hay token válido → Guarda en BD con tenant_id
    Si NO hay token → Guarda en SessionManager (memoria)
    """
    if tenant_id:
        # Usuario autenticado → persistir en BD
        await save_to_database(tenant_id, files)
    else:
        # Usuario anónimo → usar cache temporal
        session_manager.store(files)

    return {"uploaded": True}
```

### Usar TenantContext (Recomendado)

La forma **MÁS SEGURA** de trabajar con datos multi-tenant:

```python
from app.core.dependencies import get_authenticated_tenant_context
from app.database import TenantContext

@router.get("/documents")
async def list_documents(
    tenant: TenantContext = Depends(get_authenticated_tenant_context)
):
    """
    TenantContext filtra automáticamente por tenant_id

    ✅ Imposible acceder a datos de otros tenants
    ✅ No necesitas pasar tenant_id manualmente
    """
    # Todas las queries filtradas automáticamente
    documents = await tenant.get_documents(tipo_documento="compraventa")
    templates = await tenant.get_templates(include_public=True)
    preferences = await tenant.get_preferences()

    return {
        "documents": documents,
        "templates": templates,
        "preferences": preferences
    }
```

---

## 🌐 Llamadas desde el Frontend

### Con axios/fetch

```typescript
// src/api/client.ts
import axios from 'axios'
import { supabase } from '@/lib/supabase'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Interceptor para agregar token automáticamente
api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

// Uso:
const createClient = async (clientData: ClientCreateRequest) => {
  const response = await api.post('/clients', clientData)
  return response.data
}
```

### Con React Query

```typescript
// src/hooks/useClients.ts
import { useMutation } from '@tanstack/react-query'
import { api } from '@/api/client'

export const useCreateClient = () => {
  return useMutation({
    mutationFn: async (data: ClientCreateRequest) => {
      // El interceptor agrega automáticamente el token
      const response = await api.post('/clients', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] })
    }
  })
}

// Componente:
const CreateClientForm = () => {
  const { mutate, isPending } = useCreateClient()

  const handleSubmit = (data: ClientCreateRequest) => {
    mutate(data)  // Token se envía automáticamente
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

---

## 🛡️ Row Level Security (RLS)

### Políticas Automáticas

Las tablas con RLS **solo muestran datos del tenant actual**:

```sql
-- Ejemplo de política RLS en tabla 'clients'
CREATE POLICY "Users can only access their tenant's clients"
ON clients
FOR ALL
USING (
    tenant_id = (
        SELECT tenant_id
        FROM users
        WHERE id = auth.uid()
    )
);
```

### Ventajas:

- ✅ **Seguridad en BD**: Aunque el backend falle, la BD protege los datos
- ✅ **Zero Trust**: No confía en código backend solamente
- ✅ **Automático**: No requieres agregar `.eq('tenant_id', ...)` en cada query

---

## 🔍 Debugging y Testing

### Ver Token Decodificado

```python
# backend/scripts/decode_token.py
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

decoded = jwt.decode(
    token,
    options={"verify_signature": False}  # Solo para debugging
)

print(decoded)
# {
#   "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # user_id
#   "email": "admin@notaria1.mx",
#   "role": "authenticated",
#   "iat": 1234567890,
#   "exp": 1234571490
# }
```

### Probar Endpoint con cURL

```bash
# 1. Obtener token desde frontend
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Hacer request con token
curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_persona": "fisica",
    "nombre_completo": "Juan Pérez",
    "rfc": "PEGJ850101ABC",
    "email": "juan@email.com"
  }'
```

### Logs de Autenticación

```python
# El backend automáticamente loguea:

# ✅ Autenticación exitosa
{
  "event": "user_authenticated",
  "user_id": "a1b2c3d4...",
  "timestamp": "2025-01-23T10:30:00Z"
}

# ✅ Tenant recuperado
{
  "event": "tenant_retrieved",
  "user_id": "a1b2c3d4...",
  "tenant_id": "e5f6g7h8...",
  "timestamp": "2025-01-23T10:30:00Z"
}

# ❌ Token inválido
{
  "event": "authentication_failed",
  "error": "Invalid authentication credentials",
  "timestamp": "2025-01-23T10:30:05Z"
}
```

---

## ⚠️ Errores Comunes

### 401 Unauthorized

**Causa**: Token inválido o expirado

**Solución**:
```typescript
// Renovar sesión automáticamente
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    console.log('Token renovado automáticamente')
  }
})
```

### 404 User tenant not found

**Causa**: Usuario existe en Auth pero no en tabla `users`

**Solución**:
```sql
-- Verificar vinculación
SELECT u.id, u.email, u.tenant_id, t.nombre
FROM users u
LEFT JOIN tenants t ON u.tenant_id = t.id
WHERE u.id = '<USER_UUID>';

-- Si tenant_id es NULL, ejecutar setup_auth.sql
```

### CORS Error

**Causa**: Frontend en dominio no permitido

**Solución**:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://tu-dominio-produccion.com"  # Agregar producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Auditoría

### Logs Automáticos

El middleware de auditoría registra **automáticamente**:

```python
# Se registra en tabla audit_logs:
{
  "action": "create_client",
  "entity_type": "client",
  "tenant_id": "e5f6g7h8...",
  "user_id": "a1b2c3d4...",
  "details": {
    "method": "POST",
    "path": "/api/clients",
    "status_code": 201,
    "duration_ms": 124.5
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2025-01-23T10:30:00Z"
}
```

### Consultar Auditoría

```sql
-- Todas las acciones de un usuario
SELECT
    action,
    entity_type,
    details->>'path' AS endpoint,
    created_at
FROM audit_logs
WHERE user_id = '<USER_UUID>'
ORDER BY created_at DESC
LIMIT 50;

-- Acciones por tenant
SELECT
    user_id,
    action,
    COUNT(*) AS total_actions
FROM audit_logs
WHERE tenant_id = '<TENANT_UUID>'
GROUP BY user_id, action
ORDER BY total_actions DESC;
```

---

## 🚀 Próximos Pasos

1. ✅ **Setup completado**: Ya tienes autenticación funcional
2. 📱 **Implementar en Frontend**: Integrar login y manejo de tokens
3. 🔐 **Activar RLS**: Habilitar políticas en todas las tablas
4. 🧪 **Testing**: Probar flujos con usuarios reales
5. 📊 **Monitoreo**: Revisar logs de auditoría regularmente

---

## 📚 Referencias

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io Debugger](https://jwt.io/)
- [RLS Policies Guide](https://supabase.com/docs/guides/auth/row-level-security)

---

**Última actualización**: 2025-01-23
**Versión**: 2.0.0
**Autor**: ControlNot Development Team
