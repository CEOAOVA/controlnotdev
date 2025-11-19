/**
 * EmailForm Component
 * Form to send generated document via email
 */

import { useState } from 'react';
import { Mail, Loader2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useProcessDocument } from '@/hooks';
import { isValidEmail } from '@/lib/utils';

interface EmailFormProps {
  documentId: string;
  documentName?: string;
  onSuccess?: () => void;
}

export function EmailForm({ documentId, documentName, onSuccess }: EmailFormProps) {
  const [recipientEmail, setRecipientEmail] = useState('');
  const [subject, setSubject] = useState(`Documento: ${documentName || 'Sin título'}`);
  const [message, setMessage] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);
  const [sendStatus, setSendStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const { emailMutation } = useProcessDocument();

  const handleSend = async () => {
    // Validate email
    if (!recipientEmail.trim()) {
      setEmailError('El email es requerido');
      return;
    }

    if (!isValidEmail(recipientEmail)) {
      setEmailError('El email no es válido');
      return;
    }

    try {
      setEmailError(null);
      setSendStatus('idle');

      await emailMutation.mutateAsync({
        to_email: recipientEmail,
        subject: subject || `Documento: ${documentName || 'Sin título'}`,
        body: message || 'Adjunto encontrarás el documento solicitado.',
        document_id: documentId,
      });

      setSendStatus('success');
      if (onSuccess) {
        onSuccess();
      }

      // Reset form after 3 seconds
      setTimeout(() => {
        setRecipientEmail('');
        setMessage('');
        setSendStatus('idle');
      }, 3000);
    } catch (error: any) {
      console.error('Error sending email:', error);
      setSendStatus('error');
      setEmailError(error?.message || 'Error al enviar email');
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-1">Enviar por Email</h3>
        <p className="text-sm text-muted-foreground">
          El documento se enviará como archivo adjunto
        </p>
      </div>

      {/* Recipient email */}
      <div className="space-y-2">
        <Label htmlFor="email">
          Email del destinatario <span className="text-destructive">*</span>
        </Label>
        <Input
          id="email"
          type="email"
          placeholder="ejemplo@correo.com"
          value={recipientEmail}
          onChange={(e) => {
            setRecipientEmail(e.target.value);
            setEmailError(null);
          }}
          className={emailError ? 'border-destructive' : ''}
        />
        {emailError && (
          <p className="text-sm text-destructive">{emailError}</p>
        )}
      </div>

      {/* Subject */}
      <div className="space-y-2">
        <Label htmlFor="subject">Asunto</Label>
        <Input
          id="subject"
          type="text"
          placeholder="Asunto del email"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />
      </div>

      {/* Message */}
      <div className="space-y-2">
        <Label htmlFor="message">Mensaje (opcional)</Label>
        <Textarea
          id="message"
          placeholder="Escribe un mensaje personalizado..."
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
      </div>

      {/* Send button */}
      <Button
        onClick={handleSend}
        disabled={emailMutation.isPending || sendStatus === 'success'}
        className="w-full gap-2"
        size="lg"
      >
        {emailMutation.isPending ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Enviando...
          </>
        ) : sendStatus === 'success' ? (
          <>
            <CheckCircle2 className="w-5 h-5" />
            Email enviado exitosamente
          </>
        ) : (
          <>
            <Mail className="w-5 h-5" />
            Enviar Email
          </>
        )}
      </Button>

      {/* Success message */}
      {sendStatus === 'success' && (
        <Alert className="border-green-500/50 bg-green-500/10">
          <Mail className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">
            El email se envió correctamente a {recipientEmail}
          </AlertDescription>
        </Alert>
      )}

      {/* Error message */}
      {sendStatus === 'error' && (
        <Alert variant="destructive">
          <AlertDescription>
            {emailError || 'Error al enviar el email. Inténtalo de nuevo.'}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
