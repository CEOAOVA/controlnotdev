/**
 * Templates Page
 * Manage document templates with CRUD operations
 */

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Filter,
  AlertCircle,
} from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { TemplateGrid } from '@/components/templates/TemplateGrid';
import { TemplateUpload } from '@/components/templates/TemplateUpload';
import { TemplateEditor } from '@/components/templates/TemplateEditor';
import { PlaceholderMappingEditor } from '@/components/templates/PlaceholderMappingEditor';
import { useTemplates, useToast } from '@/hooks';
import type { DocumentType, TemplateInfo } from '@/store';

type ViewMode = 'grid' | 'upload';

export function Templates() {
  const {
    templates,
    isLoading,
    error,
    fetchTemplates,
    uploadTemplate,
    deleteTemplate,
    updateTemplateName,
  } = useTemplates();
  const toast = useToast();

  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<DocumentType | 'all'>('all');
  const [editingTemplate, setEditingTemplate] = useState<TemplateInfo | null>(null);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [mappingTemplate, setMappingTemplate] = useState<TemplateInfo | null>(null);
  const [isMappingEditorOpen, setIsMappingEditorOpen] = useState(false);

  // Fetch templates on mount
  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  // Filter templates
  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesType = filterType === 'all' || template.type === filterType;

    return matchesSearch && matchesType;
  });

  // Handlers
  const handleUpload = async (file: File, name: string, type: DocumentType) => {
    try {
      await uploadTemplate(file, name, type);
      toast.success(`Template "${name}" subido exitosamente`);
      setViewMode('grid');
    } catch (err: any) {
      toast.error(`Error al subir template: ${err.message}`);
    }
  };

  const handleEdit = (template: TemplateInfo) => {
    setEditingTemplate(template);
    setIsEditorOpen(true);
  };

  const handleSaveEdit = async (id: string, name: string, _type: DocumentType) => {
    try {
      await updateTemplateName(id, name);
      toast.success('Template actualizado exitosamente');
      setIsEditorOpen(false);
      setEditingTemplate(null);
      fetchTemplates(); // Refresh list
    } catch (err: any) {
      toast.error(`Error al actualizar template: ${err.message}`);
    }
  };

  const handleDelete = async (template: TemplateInfo) => {
    if (
      confirm(
        `¿Estás seguro de que deseas eliminar el template "${template.name}"?`
      )
    ) {
      try {
        await deleteTemplate(template.id);
        toast.success(`Template "${template.name}" eliminado`);
      } catch (err: any) {
        toast.error(`Error al eliminar template: ${err.message}`);
      }
    }
  };

  const handleDuplicate = async (template: TemplateInfo) => {
    // TODO: Implement duplicate functionality
    console.log('Duplicate template:', template);
    toast.error('Funcionalidad de duplicar en desarrollo');
  };

  const handleDownload = async (template: TemplateInfo) => {
    // TODO: Implement download functionality
    console.log('Download template:', template);
    toast.error('Funcionalidad de descarga en desarrollo');
  };

  const handleEditMapping = (template: TemplateInfo) => {
    setMappingTemplate(template);
    setIsMappingEditorOpen(true);
  };

  const handleMappingSaved = () => {
    toast.success('Mapeo actualizado exitosamente');
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900">Templates</h1>
            <p className="text-neutral-600 mt-1">
              Gestiona los templates de documentos para tu notaría
            </p>
          </div>
          <Button
            size="lg"
            className="gap-2"
            onClick={() =>
              setViewMode(viewMode === 'grid' ? 'upload' : 'grid')
            }
          >
            {viewMode === 'grid' ? (
              <>
                <Plus className="w-5 h-5" />
                Subir Template
              </>
            ) : (
              <>
                <Filter className="w-5 h-5" />
                Ver Templates
              </>
            )}
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Upload View */}
        {viewMode === 'upload' && (
          <TemplateUpload
            onUpload={handleUpload}
            onCancel={() => setViewMode('grid')}
            isLoading={isLoading}
          />
        )}

        {/* Grid View */}
        {viewMode === 'grid' && (
          <>
            {/* Filters */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <Input
                  type="search"
                  placeholder="Buscar templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>

              {/* Type Filter */}
              <Select
                value={filterType}
                onValueChange={(value) =>
                  setFilterType(value as DocumentType | 'all')
                }
              >
                <SelectTrigger className="w-full sm:w-[200px]">
                  <SelectValue placeholder="Filtrar por tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  <SelectItem value="compraventa">Compraventa</SelectItem>
                  <SelectItem value="donacion">Donación</SelectItem>
                  <SelectItem value="testamento">Testamento</SelectItem>
                  <SelectItem value="poder">Poder</SelectItem>
                  <SelectItem value="sociedad">Sociedad</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <span>
                Mostrando {filteredTemplates.length} de {templates.length}{' '}
                templates
              </span>
            </div>

            {/* Templates Grid */}
            <TemplateGrid
              templates={filteredTemplates}
              onEdit={handleEdit}
              onEditMapping={handleEditMapping}
              onDelete={handleDelete}
              onDownload={handleDownload}
              onDuplicate={handleDuplicate}
              isLoading={isLoading}
            />
          </>
        )}

        {/* Template Editor Dialog */}
        <TemplateEditor
          template={editingTemplate}
          isOpen={isEditorOpen}
          onClose={() => {
            setIsEditorOpen(false);
            setEditingTemplate(null);
          }}
          onSave={handleSaveEdit}
          isLoading={isLoading}
        />

        {/* Placeholder Mapping Editor Dialog */}
        {mappingTemplate && (
          <PlaceholderMappingEditor
            templateId={mappingTemplate.id}
            templateName={mappingTemplate.name}
            isOpen={isMappingEditorOpen}
            onClose={() => {
              setIsMappingEditorOpen(false);
              setMappingTemplate(null);
            }}
            onSaved={handleMappingSaved}
          />
        )}
      </div>
    </MainLayout>
  );
}
