/**
 * ImagePreview Component
 * Display file preview with thumbnail and info
 */

import { useState } from 'react';
import { X, FileText, ZoomIn } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { formatBytes } from '@/lib/utils';
import type { UploadedFile } from '@/store';

interface ImagePreviewProps {
  uploadedFile: UploadedFile;
  onRemove: () => void;
  showRemove?: boolean;
}

export function ImagePreview({
  uploadedFile,
  onRemove,
  showRemove = true,
}: ImagePreviewProps) {
  const [showFullImage, setShowFullImage] = useState(false);
  const { file, preview } = uploadedFile;

  const isImage = file.type.startsWith('image/');
  const isPDF = file.type === 'application/pdf';

  return (
    <>
      <div className="relative group rounded-lg border bg-card overflow-hidden hover:shadow-md transition-shadow">
        {/* Preview */}
        <div
          className="aspect-square bg-muted flex items-center justify-center cursor-pointer"
          onClick={() => isImage && setShowFullImage(true)}
        >
          {isImage && preview ? (
            <img
              src={preview}
              alt={file.name}
              className="w-full h-full object-cover"
            />
          ) : isPDF ? (
            <FileText className="w-16 h-16 text-muted-foreground" />
          ) : (
            <FileText className="w-16 h-16 text-muted-foreground" />
          )}

          {/* Zoom overlay for images */}
          {isImage && (
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <ZoomIn className="w-8 h-8 text-white" />
            </div>
          )}
        </div>

        {/* File info */}
        <div className="p-2 space-y-1">
          <p className="text-xs font-medium truncate" title={file.name}>
            {file.name}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatBytes(file.size)}
          </p>
        </div>

        {/* Remove button */}
        {showRemove && (
          <Button
            variant="destructive"
            size="icon"
            className="absolute top-2 right-2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      {/* Full image dialog */}
      {isImage && preview && (
        <Dialog open={showFullImage} onOpenChange={setShowFullImage}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>{file.name}</DialogTitle>
            </DialogHeader>
            <div className="max-h-[70vh] overflow-auto">
              <img
                src={preview}
                alt={file.name}
                className="w-full h-auto"
              />
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
