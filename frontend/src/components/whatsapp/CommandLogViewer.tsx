/**
 * CommandLogViewer
 * Read-only table showing staff command log with filters
 */

import { useState, useEffect } from 'react';
import { Terminal, RefreshCw, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { whatsappApi } from '@/api/endpoints/whatsapp';
import { useToast } from '@/hooks/useToast';
import type { WACommandLog } from '@/api/types/whatsapp-types';

export function CommandLogViewer() {
  const [logs, setLogs] = useState<WACommandLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [phoneFilter, setPhoneFilter] = useState('');
  const toast = useToast();

  const loadLogs = async () => {
    setIsLoading(true);
    try {
      const data = await whatsappApi.listCommandLog({
        staff_phone: phoneFilter || undefined,
        limit: 100,
      });
      setLogs(data);
    } catch (err) {
      console.error('Error loading command log:', err);
      toast.error('Error al cargar log de comandos');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const handleClearFilter = () => {
    setPhoneFilter('');
    loadLogs();
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-MX', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-lg">Log de Comandos</h3>
        </div>
        <div className="flex gap-2">
          <Input
            placeholder="Filtrar por telefono..."
            value={phoneFilter}
            onChange={(e) => setPhoneFilter(e.target.value)}
            className="w-48"
            onKeyDown={(e) => e.key === 'Enter' && loadLogs()}
          />
          {phoneFilter && (
            <Button size="sm" variant="ghost" onClick={handleClearFilter} title="Limpiar filtro">
              <XCircle className="w-4 h-4" />
            </Button>
          )}
          <Button size="sm" variant="outline" onClick={loadLogs} disabled={isLoading} className="gap-1">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="max-h-[500px] overflow-y-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Fecha</TableHead>
              <TableHead>Telefono</TableHead>
              <TableHead>Comando</TableHead>
              <TableHead>Resultado</TableHead>
              <TableHead>Preview</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-neutral-500">
                  Cargando...
                </TableCell>
              </TableRow>
            ) : logs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-neutral-500">
                  No hay registros en el log
                </TableCell>
              </TableRow>
            ) : (
              logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="text-xs text-neutral-500 whitespace-nowrap">
                    {formatDate(log.created_at)}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{log.staff_phone}</TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="font-mono text-xs">
                      {log.command}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {log.result === 'ok' ? (
                      <Badge variant="outline" className="text-green-600 border-green-200">OK</Badge>
                    ) : (
                      <Badge variant="outline" className="text-red-600 border-red-200">
                        {log.result || '—'}
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-xs text-neutral-500 max-w-xs truncate">
                    {log.response_preview || '—'}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}
