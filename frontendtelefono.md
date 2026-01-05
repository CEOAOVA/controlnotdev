 Resumen del Plan

  15 archivos/pasos a modificar:
  1. Config: tailwind.config.js, globals.css
  2. Layout: MainLayout.tsx, Sidebar.tsx, Topbar.tsx + nuevo useSidebarStore.ts
  3. Upload: UnifiedUploader.tsx, CategoryTab.tsx, DropZone.tsx, ImagePreview.tsx
  4. Otros: ProgressIndicator.tsx, DataEditor.tsx, PreviewModal.tsx, DocumentPreview.tsx

  Decisiones confirmadas:
  - Tabs: Scroll horizontal con scrollbar-hide
  - Sidebar: Overlay con backdrop oscuro + slide-in animation

● User approved Claude's plan
  ⎿  Plan saved to: ~\.claude\plans\crystalline-hatching-tower.md · /plan to edit
     Plan: Adaptación Móvil del Frontend ControlNot v2

     Objetivo

     Adaptar el grid y componentes del frontend para funcionar correctamente en dispositivos móviles, eliminando overlaps, mejorando la carga de imágenes y      
     asegurando una experiencia touch-friendly.

     ---
     Problemas Identificados

     CRÍTICOS (Bloquean uso móvil)

     | Archivo               | Línea  | Problema                                                        |
     |-----------------------|--------|-----------------------------------------------------------------|
     | MainLayout.tsx        | 26     | Sidebar fixed ml-64 sin responsive - bloquea contenido en móvil |
     | UnifiedUploader.tsx   | 286    | TabsList grid-cols-3 fijo - tabs se cortan en móvil             |
     | ProgressIndicator.tsx | 66-135 | Labels max-w-[120px] fijos - se solapan en móvil                |

     IMPORTANTES (UX degradada)

     | Archivo             | Línea | Problema                                          |
     |---------------------|-------|---------------------------------------------------|
     | CategoryTab.tsx     | 97    | Grid grid-cols-2 mínimo - muy pequeño en <375px   |
     | DataEditor.tsx      | 195   | Stats grid-cols-3 sin responsive                  |
     | DropZone.tsx        | 49-54 | Padding p-8 fijo - mucho espacio en móvil         |
     | DocumentPreview.tsx | 182   | Height h-[400px] fijo                             |
     | PreviewModal.tsx    | 73    | max-w-4xl sin fullscreen móvil                    |
     | ImagePreview.tsx    | -     | Botón eliminar h-6 w-6 (24px) < 44px touch target |

     ---
     Archivos a Modificar

     frontend/src/
     ├── components/
     │   ├── layout/
     │   │   ├── MainLayout.tsx        ← CRÍTICO: Sidebar responsive
     │   │   ├── Sidebar.tsx           ← Hamburger menu móvil
     │   │   └── Topbar.tsx            ← Toggle sidebar móvil
     │   ├── upload/
     │   │   ├── UnifiedUploader.tsx   ← Tabs scrollable/stacked
     │   │   ├── CategoryTab.tsx       ← Grid 1 col en xs
     │   │   ├── DropZone.tsx          ← Padding responsive
     │   │   └── ImagePreview.tsx      ← Touch targets 44px
     │   ├── progress/
     │   │   └── ProgressIndicator.tsx ← Compacto en móvil
     │   ├── editor/
     │   │   └── DataEditor.tsx        ← Stats responsive
     │   └── document/
     │       ├── DocumentPreview.tsx   ← Height responsive
     │       └── PreviewModal.tsx      ← Fullscreen móvil
     └── styles/
         └── globals.css               ← Breakpoint xs: 375px

     ---
     Plan de Implementación

     FASE 1: Layout Principal (MainLayout + Sidebar)

     Cambios en MainLayout.tsx:
     // ANTES
     <div className={`flex-1 flex flex-col ${!fullWidth ? 'ml-64' : ''}`}>

     // DESPUÉS
     <div className={`flex-1 flex flex-col ${!fullWidth ? 'md:ml-64' : ''}`}>

     Cambios en Sidebar.tsx: (Overlay con backdrop - elegido por usuario)
     // Wrapper con overlay backdrop
     <>
       {/* Backdrop oscuro */}
       {isOpen && (
         <div
           className="fixed inset-0 bg-black/50 z-40 md:hidden"
           onClick={onClose}
         />
       )}

       {/* Sidebar */}
       <aside className={cn(
         "fixed left-0 top-0 h-screen bg-white z-50",
         "w-64 transition-transform duration-300",
         // Desktop: siempre visible
         "md:translate-x-0",
         // Mobile: slide-in
         isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
       )}>
         {/* Botón cerrar - solo móvil */}
         <Button
           variant="ghost"
           className="absolute top-4 right-4 md:hidden"
           onClick={onClose}
         >
           <X className="h-5 w-5" />
         </Button>
         ...
       </aside>
     </>

     Cambios en Topbar.tsx:
     // Agregar botón hamburger al inicio del Topbar
     <Button
       variant="ghost"
       size="icon"
       className="md:hidden mr-2"
       onClick={toggleSidebar}
     >
       <Menu className="h-5 w-5" />
     </Button>

     Crear contexto/store para sidebar:
     // store/useSidebarStore.ts
     export const useSidebarStore = create<SidebarState>((set) => ({
       isOpen: false,
       toggle: () => set((state) => ({ isOpen: !state.isOpen })),
       close: () => set({ isOpen: false }),
     }))

     FASE 2: Sistema de Tabs (UnifiedUploader)

     Cambios en UnifiedUploader.tsx:
     // ANTES
     <TabsList className="grid w-full grid-cols-3">

     // DESPUÉS - Scroll horizontal (elegido por usuario)
     <TabsList className="flex w-full overflow-x-auto scrollbar-hide gap-1">
       <TabsTrigger className="flex-shrink-0 min-w-fit">...</TabsTrigger>

     Agregar CSS en globals.css:
     .scrollbar-hide {
       -ms-overflow-style: none;
       scrollbar-width: none;
     }
     .scrollbar-hide::-webkit-scrollbar {
       display: none;
     }

     FASE 3: Progress Indicator

     Cambios en ProgressIndicator.tsx:
     - Móvil: Solo mostrar números y línea de progreso
     - Ocultar labels y descripciones: hidden sm:block
     - Alternativa: Steps verticales en móvil

     // Labels
     <span className="hidden sm:inline text-sm">{step.label}</span>

     // Descripción
     <span className="hidden md:block text-xs">{step.description}</span>

     FASE 4: Grids de Imágenes (CategoryTab)

     Cambios en CategoryTab.tsx:
     // ANTES
     className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"

     // DESPUÉS - Incluir caso xs
     className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4"

     Agregar breakpoint xs en tailwind.config.js:
     theme: {
       screens: {
         'xs': '375px',
         'sm': '640px',
         // ...
       }
     }

     FASE 5: DropZone Responsive

     Cambios en DropZone.tsx:
     // ANTES
     className="border-2 border-dashed rounded-lg p-8 text-center"

     // DESPUÉS
     className="border-2 border-dashed rounded-lg p-4 sm:p-8 text-center"

     // Icono
     <Upload className="h-8 w-8 sm:h-12 sm:w-12 mx-auto" />

     // Texto
     <p className="text-sm sm:text-base">Arrastra archivos aquí</p>

     FASE 6: Touch Targets

     Cambios en ImagePreview.tsx:
     // ANTES - Botón eliminar
     <Button size="icon" className="h-6 w-6">

     // DESPUÉS - Mínimo 44px para touch
     <Button size="icon" className="h-8 w-8 sm:h-6 sm:w-6">

     FASE 7: DataEditor Stats

     Cambios en DataEditor.tsx:
     // ANTES
     <div className="grid grid-cols-3 gap-3">

     // DESPUÉS
     <div className="grid grid-cols-1 xs:grid-cols-3 gap-2 sm:gap-3">

     FASE 8: Modales Fullscreen

     Cambios en PreviewModal.tsx:
     // ANTES
     <DialogContent className="max-w-4xl max-h-[80vh]">

     // DESPUÉS
     <DialogContent className="w-full h-full sm:max-w-4xl sm:max-h-[80vh] sm:h-auto">

     Cambios en DocumentPreview.tsx:
     // ANTES
     <ScrollArea className="h-[400px]">

     // DESPUÉS
     <ScrollArea className="h-[60vh] sm:h-[400px]">

     ---
     Orden de Ejecución

     1. Tailwind config - Agregar breakpoint xs: 375px
     2. globals.css - Agregar clase scrollbar-hide
     3. useSidebarStore.ts - Crear store para estado del sidebar
     4. MainLayout.tsx - Agregar md:ml-64 responsive
     5. Sidebar.tsx - Overlay con backdrop y animación slide-in
     6. Topbar.tsx - Hamburger button con toggle
     7. ProgressIndicator.tsx - Labels compactos/ocultos en móvil
     8. UnifiedUploader.tsx - Tabs scroll horizontal
     9. CategoryTab.tsx - Grid 1 col xs, 2 cols sm
     10. DropZone.tsx - Padding responsive p-4 sm:p-8
     11. ImagePreview.tsx - Touch targets h-8 w-8
     12. DataEditor.tsx - Stats grid responsive
     13. PreviewModal.tsx - Fullscreen móvil
     14. DocumentPreview.tsx - Height h-[60vh] sm:h-[400px]
     15. Verificación - Test en 375px, 640px, 768px + npm run build

     ---
     Breakpoints Objetivo

     | Breakpoint | Ancho  | Comportamiento                    |
     |------------|--------|-----------------------------------|
     | xs (nuevo) | 375px  | iPhone SE, móviles pequeños       |
     | sm         | 640px  | Móviles grandes, tablets portrait |
     | md         | 768px  | Tablets, laptops pequeñas         |
     | lg         | 1024px | Laptops, desktops                 |

     ---
     Verificación Final

     - Sidebar se oculta/muestra con hamburger en móvil
     - Tabs no se cortan ni solapan
     - Progress indicator es legible
     - Grids de imágenes se adaptan correctamente
     - Touch targets ≥ 44px
     - Modales usan fullscreen en móvil
     - Sin overlaps en ningún breakpoint
     - Upload de imágenes funciona con touch
     - npm run build compila sin errores