# ControlNot v2 - Frontend

Frontend moderno para el sistema de procesamiento de documentos notariales con IA.

## Stack Tecnológico

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI**: Tailwind CSS + shadcn/ui
- **Estado**: Zustand + React Query
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **File Handling**: React Dropzone
- **Icons**: Lucide React
- **Routing**: React Router v6

## Instalación

```bash
# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env.local

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## Scripts Disponibles

```bash
npm run dev        # Servidor de desarrollo
npm run build      # Build para producción
npm run preview    # Preview del build
npm run lint       # Linting con ESLint
npm run format     # Formatear código con Prettier
```

## Estructura del Proyecto

```
src/
├── api/              # API client y endpoints
├── components/       # Componentes React
│   ├── ui/          # shadcn/ui components
│   ├── layout/      # Layout components
│   ├── templates/   # Template components
│   ├── documents/   # Document components
│   ├── extraction/  # Extraction components
│   └── shared/      # Shared components
├── pages/           # Páginas de la aplicación
├── features/        # Features complejas
├── hooks/           # Custom React hooks
├── store/           # Zustand store
├── utils/           # Utilidades
├── styles/          # Estilos globales
└── types/           # TypeScript types
```

## Integración con Backend

El frontend se comunica con el backend FastAPI en `http://localhost:8000`.

La configuración de proxy en Vite redirige todas las peticiones `/api/*` al backend automáticamente.

## Workflow Principal

1. **Template Selection** - Seleccionar o subir template Word
2. **Document Upload** - Subir documentos categorizados (Parte A, B, Otros)
3. **OCR Processing** - Procesamiento OCR asíncrono paralelo
4. **AI Extraction** - Extracción de datos con IA
5. **Data Review** - Revisar y editar datos extraídos
6. **Generation** - Generar documento final y descargar

## Features

✅ Workflow lineal guiado con step indicator  
✅ Drag & drop multi-file upload  
✅ Progress indicators en tiempo real  
✅ Edición inline de datos extraídos  
✅ Validación de formularios con Zod  
✅ Error handling global  
✅ Diseño responsive  
✅ Dark mode ready  
✅ Accesibilidad WCAG AA  

## Desarrollo

### Requisitos

- Node.js 18+
- npm o yarn
- Backend FastAPI corriendo en puerto 8000

### Variables de Entorno

Ver `.env.example` para las variables necesarias.

## Build para Producción

```bash
# Crear build optimizado
npm run build

# El build estará en la carpeta dist/
# Puedes servir con cualquier servidor estático
```

## Licencia

Parte del proyecto ControlNot v2
