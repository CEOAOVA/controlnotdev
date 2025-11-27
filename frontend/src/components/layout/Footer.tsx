/**
 * Footer Component
 * Application footer with version only
 */

export function Footer() {
  return (
    <footer className="border-t bg-muted/30 mt-auto">
      <div className="container py-4">
        <p className="text-center text-xs text-muted-foreground">
          v2.0.0
        </p>
      </div>
    </footer>
  );
}
