/**
 * CaseDetailPage
 * Full case detail with workflow bar, transition buttons, and 6 tabs
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Play, FileText } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CaseStatusBadge } from '@/components/cases/CaseStatusBadge';
import { CasePriorityBadge } from '@/components/cases/CasePriorityBadge';
import { WorkflowBar } from '@/components/cases/WorkflowBar';
import { TransitionButtons } from '@/components/cases/TransitionButtons';
import { CaseEditForm } from '@/components/cases/CaseEditForm';
import { PartyList } from '@/components/parties/PartyList';
import { ChecklistPanel } from '@/components/checklist/ChecklistPanel';
import { TramiteList } from '@/components/tramites/TramiteList';
import { ActivityTimeline } from '@/components/timeline/ActivityTimeline';
import { NoteInput } from '@/components/timeline/NoteInput';
import { useCases } from '@/hooks';
import { useToast } from '@/hooks';
import {
  casesApi,
  partiesApi,
  checklistApi,
  tramitesApi,
  timelineApi,
} from '@/api/endpoints/cases';
import type {
  CaseParty,
  ChecklistItem,
  Tramite,
  CaseTimeline,
  CaseUpdateRequest,
  PartyCreateRequest,
  TramiteCreateRequest,
  ChecklistStatus,
} from '@/api/types/cases-types';

export function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const toast = useToast();
  const { selectedCase, isLoading, error, fetchCaseById } = useCases();

  // Tab data loaded lazily
  const [parties, setParties] = useState<CaseParty[]>([]);
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([]);
  const [tramites, setTramites] = useState<Tramite[]>([]);
  const [timeline, setTimeline] = useState<CaseTimeline | null>(null);
  const [caseDocuments, setCaseDocuments] = useState<any[]>([]);

  const [activeTab, setActiveTab] = useState('resumen');

  // Load case detail on mount
  useEffect(() => {
    if (caseId) {
      fetchCaseById(caseId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  // Set parties from case detail (comes pre-loaded)
  useEffect(() => {
    if (selectedCase) {
      setParties(selectedCase.case_parties || []);
    }
  }, [selectedCase]);

  // Lazy load tab data
  useEffect(() => {
    if (!caseId) return;

    if (activeTab === 'checklist') {
      checklistApi.list(caseId).then(setChecklistItems).catch(console.error);
    } else if (activeTab === 'tramites') {
      tramitesApi.list(caseId).then(setTramites).catch(console.error);
    } else if (activeTab === 'timeline') {
      timelineApi.get(caseId).then(setTimeline).catch(console.error);
    } else if (activeTab === 'documentos') {
      casesApi.getDocuments(caseId).then((r) => setCaseDocuments(r.documents || [])).catch(console.error);
    }
  }, [activeTab, caseId]);

  const reloadCase = useCallback(() => {
    if (caseId) fetchCaseById(caseId);
  }, [caseId, fetchCaseById]);

  // === Handlers ===

  const handleTransition = async (status: string, notes?: string) => {
    if (!caseId) return;
    try {
      await casesApi.transition(caseId, status, notes);
      toast.success('Estado actualizado');
      reloadCase();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error en transicion');
    }
  };

  const handleResume = async () => {
    if (!caseId) return;
    try {
      await casesApi.resume(caseId);
      toast.success('Expediente reanudado');
      reloadCase();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al reanudar');
    }
  };

  const handleUpdateCase = async (data: CaseUpdateRequest) => {
    if (!caseId) return;
    try {
      await casesApi.update(caseId, data);
      toast.success('Expediente actualizado');
      reloadCase();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al actualizar');
    }
  };

  // Parties
  const handleAddParty = async (data: PartyCreateRequest) => {
    if (!caseId) return;
    const party = await partiesApi.create(caseId, data);
    setParties((prev) => [...prev, party]);
    toast.success('Parte agregada');
  };

  const handleUpdateParty = async (partyId: string, data: Record<string, any>) => {
    if (!caseId) return;
    const updated = await partiesApi.update(caseId, partyId, data);
    setParties((prev) => prev.map((p) => (p.id === partyId ? updated : p)));
    toast.success('Parte actualizada');
  };

  const handleRemoveParty = async (partyId: string) => {
    if (!caseId) return;
    await partiesApi.remove(caseId, partyId);
    setParties((prev) => prev.filter((p) => p.id !== partyId));
    toast.success('Parte eliminada');
  };

  // Checklist
  const handleInitializeChecklist = async () => {
    if (!caseId || !selectedCase) return;
    const items = await checklistApi.initialize(caseId, selectedCase.document_type);
    setChecklistItems(items);
    toast.success('Checklist inicializado');
    reloadCase();
  };

  const handleChecklistStatusChange = async (itemId: string, status: ChecklistStatus) => {
    if (!caseId) return;
    const updated = await checklistApi.updateStatus(caseId, itemId, status);
    setChecklistItems((prev) => prev.map((i) => (i.id === itemId ? updated : i)));
    reloadCase();
  };

  const handleRemoveChecklistItem = async (itemId: string) => {
    if (!caseId) return;
    await checklistApi.remove(caseId, itemId);
    setChecklistItems((prev) => prev.filter((i) => i.id !== itemId));
    reloadCase();
  };

  // Tramites
  const handleAddTramite = async (data: TramiteCreateRequest) => {
    if (!caseId) return;
    const tramite = await tramitesApi.create(caseId, data);
    setTramites((prev) => [...prev, tramite]);
    toast.success('Tramite creado');
  };

  const handleUpdateTramite = async (tramiteId: string, data: Record<string, any>) => {
    if (!caseId) return;
    const updated = await tramitesApi.update(caseId, tramiteId, data);
    setTramites((prev) => prev.map((t) => (t.id === tramiteId ? updated : t)));
    toast.success('Tramite actualizado');
  };

  const handleCompleteTramite = async (tramiteId: string) => {
    if (!caseId) return;
    const completed = await tramitesApi.complete(caseId, tramiteId);
    setTramites((prev) => prev.map((t) => (t.id === tramiteId ? completed : t)));
    toast.success('Tramite completado');
  };

  const handleRemoveTramite = async (tramiteId: string) => {
    if (!caseId) return;
    await tramitesApi.remove(caseId, tramiteId);
    setTramites((prev) => prev.filter((t) => t.id !== tramiteId));
    toast.success('Tramite eliminado');
  };

  // Timeline
  const handleAddNote = async (note: string) => {
    if (!caseId) return;
    await timelineApi.addNote(caseId, note);
    toast.success('Nota agregada');
    const updated = await timelineApi.get(caseId);
    setTimeline(updated);
  };

  // === Render ===

  if (isLoading && !selectedCase) {
    return (
      <MainLayout>
        <div className="space-y-4">
          <div className="h-8 bg-neutral-200 rounded w-1/3 animate-pulse" />
          <div className="h-16 bg-neutral-200 rounded animate-pulse" />
          <div className="h-64 bg-neutral-200 rounded animate-pulse" />
        </div>
      </MainLayout>
    );
  }

  if (error && !selectedCase) {
    return (
      <MainLayout>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Link to="/cases" className="mt-4 inline-block">
          <Button variant="outline" className="gap-2">
            <ArrowLeft className="w-4 h-4" /> Volver a Expedientes
          </Button>
        </Link>
      </MainLayout>
    );
  }

  if (!selectedCase) return null;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Back + Header */}
        <div className="flex items-start gap-4">
          <Link to="/cases">
            <Button variant="ghost" size="icon" className="mt-1">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-neutral-900">
                {selectedCase.case_number}
              </h1>
              <CaseStatusBadge status={selectedCase.status} />
              {selectedCase.priority && <CasePriorityBadge priority={selectedCase.priority} />}
            </div>
            {selectedCase.description && (
              <p className="text-neutral-600 mt-1">{selectedCase.description}</p>
            )}
          </div>
        </div>

        {/* Workflow Bar */}
        <Card className="p-4">
          <WorkflowBar currentStatus={selectedCase.status} />
        </Card>

        {/* Transition Buttons + Resume */}
        <div className="flex flex-wrap items-center gap-3">
          <TransitionButtons
            transitions={selectedCase.available_transitions}
            onTransition={handleTransition}
            isLoading={isLoading}
          />
          {selectedCase.status === 'suspendido' && (
            <Button variant="outline" className="gap-1" onClick={handleResume}>
              <Play className="w-4 h-4" />
              Reanudar
            </Button>
          )}
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 md:grid-cols-6">
            <TabsTrigger value="resumen">Resumen</TabsTrigger>
            <TabsTrigger value="partes">Partes</TabsTrigger>
            <TabsTrigger value="checklist">Checklist</TabsTrigger>
            <TabsTrigger value="tramites">Tramites</TabsTrigger>
            <TabsTrigger value="documentos">Documentos</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="resumen" className="mt-6">
            <CaseEditForm caseData={selectedCase} onSave={handleUpdateCase} />
          </TabsContent>

          <TabsContent value="partes" className="mt-6">
            <PartyList
              parties={parties}
              onAdd={handleAddParty}
              onUpdate={handleUpdateParty}
              onRemove={handleRemoveParty}
            />
          </TabsContent>

          <TabsContent value="checklist" className="mt-6">
            <ChecklistPanel
              items={checklistItems}
              summary={selectedCase.checklist_summary || undefined}
              onInitialize={handleInitializeChecklist}
              onStatusChange={handleChecklistStatusChange}
              onRemove={handleRemoveChecklistItem}
            />
          </TabsContent>

          <TabsContent value="tramites" className="mt-6">
            <TramiteList
              tramites={tramites}
              onAdd={handleAddTramite}
              onUpdate={handleUpdateTramite}
              onComplete={handleCompleteTramite}
              onRemove={handleRemoveTramite}
            />
          </TabsContent>

          <TabsContent value="documentos" className="mt-6">
            {caseDocuments.length === 0 ? (
              <Card className="p-8">
                <div className="text-center space-y-2">
                  <FileText className="w-10 h-10 text-neutral-400 mx-auto" />
                  <p className="text-neutral-600">No hay documentos generados para este expediente</p>
                </div>
              </Card>
            ) : (
              <Card>
                <div className="divide-y divide-neutral-200">
                  {caseDocuments.map((doc: any) => (
                    <div key={doc.id} className="p-4 hover:bg-neutral-50">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-primary-600" />
                        <div>
                          <p className="font-medium text-neutral-900">{doc.nombre_documento || doc.name || 'Documento'}</p>
                          <p className="text-xs text-neutral-500">{doc.tipo_documento || doc.type || ''}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="timeline" className="mt-6 space-y-4">
            <NoteInput onSubmit={handleAddNote} />
            <ActivityTimeline timeline={timeline} />
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
