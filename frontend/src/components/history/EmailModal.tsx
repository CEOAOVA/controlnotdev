/**
 * EmailModal Component
 * Modal to send a document via email with proper validation
 */

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Mail,
  Send,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

interface DocumentToEmail {
  id: string;
  name: string;
}

interface EmailModalProps {
  document: DocumentToEmail | null;
  isOpen: boolean;
  onClose: () => void;
  onSend: (data: { document_id: string; to_email: string; subject: string; body?: string }) => Promise<void>;
}

// Simple email validation regex
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function EmailModal({
  document,
  isOpen,
  onClose,
  onSend,
}: EmailModalProps) {
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [touched, setTouched] = useState({ email: false, subject: false });

  // Reset form when document changes or modal opens
  useEffect(() => {
    if (document && isOpen) {
      setSubject(`Documento: ${document.name}`);
      setBody(`Adjunto el documento "${document.name}" para su revision.`);
      setEmail('');
      setError(null);
      setSuccess(false);
      setTouched({ email: false, subject: false });
    }
  }, [document, isOpen]);

  const validateEmail = (value: string): boolean => {
    return EMAIL_REGEX.test(value);
  };

  const emailError = touched.email && !validateEmail(email)
    ? 'Ingresa un email valido'
    : null;

  const subjectError = touched.subject && !subject.trim()
    ? 'El asunto es requerido'
    : null;

  const isValid = validateEmail(email) && subject.trim().length > 0;

  const handleSend = async () => {
    if (!document || !isValid) return;

    setIsSending(true);
    setError(null);

    try {
      await onSend({
        document_id: document.id,
        to_email: email,
        subject: subject,
        body: body || undefined,
      });
      setSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al enviar email');
    } finally {
      setIsSending(false);
    }
  };

  const handleClose = () => {
    if (isSending) return;
    setEmail('');
    setSubject('');
    setBody('');
    setError(null);
    setSuccess(false);
    setTouched({ email: false, subject: false });
    onClose();
  };

  if (!document) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5" />
            Enviar por Email
          </DialogTitle>
          <DialogDescription>
            Enviar <span className="font-medium">{document.name}</span> por correo electronico
          </DialogDescription>
        </DialogHeader>

        {/* Success State */}
        {success && (
          <div className="py-8 text-center space-y-3">
            <div className="w-16 h-16 bg-success-50 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-neutral-900">
                Email Enviado
              </h3>
              <p className="text-neutral-600">
                El documento ha sido enviado a {email}
              </p>
            </div>
          </div>
        )}

        {/* Form State */}
        {!success && (
          <>
            {/* Error Alert */}
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertTriangle className="w-4 h-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              {/* Email Input */}
              <div className="space-y-2">
                <Label htmlFor="email">
                  Email del destinatario <span className="text-error">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="ejemplo@correo.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => setTouched((prev) => ({ ...prev, email: true }))}
                  disabled={isSending}
                  className={emailError ? 'border-error focus-visible:ring-error' : ''}
                />
                {emailError && (
                  <p className="text-sm text-error">{emailError}</p>
                )}
              </div>

              {/* Subject Input */}
              <div className="space-y-2">
                <Label htmlFor="subject">
                  Asunto <span className="text-error">*</span>
                </Label>
                <Input
                  id="subject"
                  type="text"
                  placeholder="Asunto del correo"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  onBlur={() => setTouched((prev) => ({ ...prev, subject: true }))}
                  disabled={isSending}
                  className={subjectError ? 'border-error focus-visible:ring-error' : ''}
                />
                {subjectError && (
                  <p className="text-sm text-error">{subjectError}</p>
                )}
              </div>

              {/* Body Textarea */}
              <div className="space-y-2">
                <Label htmlFor="body">Mensaje (opcional)</Label>
                <Textarea
                  id="body"
                  placeholder="Escribe un mensaje..."
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  disabled={isSending}
                  rows={3}
                />
              </div>
            </div>
          </>
        )}

        <DialogFooter className="mt-4">
          {!success && (
            <>
              <Button variant="outline" onClick={handleClose} disabled={isSending}>
                Cancelar
              </Button>
              <Button
                onClick={handleSend}
                disabled={!isValid || isSending}
                className="gap-2"
              >
                {isSending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Enviar
                  </>
                )}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
