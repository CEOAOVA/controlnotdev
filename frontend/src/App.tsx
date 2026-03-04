import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthGuard } from './components/auth/AuthGuard';

// Lazy-loaded pages
const ProcessPage = lazy(() => import('./pages/ProcessPage').then(m => ({ default: m.ProcessPage })));
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Templates = lazy(() => import('./pages/Templates').then(m => ({ default: m.Templates })));
const History = lazy(() => import('./pages/History').then(m => ({ default: m.History })));
const Settings = lazy(() => import('./pages/Settings').then(m => ({ default: m.Settings })));
const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const CasesPage = lazy(() => import('./pages/CasesPage').then(m => ({ default: m.CasesPage })));
const CaseDetailPage = lazy(() => import('./pages/CaseDetailPage').then(m => ({ default: m.CaseDetailPage })));
const CalendarPage = lazy(() => import('./pages/CalendarPage').then(m => ({ default: m.CalendarPage })));
const ReportsPage = lazy(() => import('./pages/ReportsPage').then(m => ({ default: m.ReportsPage })));
const UIFPage = lazy(() => import('./pages/UIFPage').then(m => ({ default: m.UIFPage })));
const WhatsAppPage = lazy(() => import('./pages/WhatsAppPage').then(m => ({ default: m.WhatsAppPage })));

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-neutral-900" />
    </div>
  );
}

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#171717',
            border: '1px solid #e5e5e5',
            padding: '16px',
            borderRadius: '8px',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<Login />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <AuthGuard>
                <Dashboard />
              </AuthGuard>
            }
          />
          <Route
            path="/generate"
            element={
              <AuthGuard>
                <ProcessPage />
              </AuthGuard>
            }
          />
          <Route
            path="/templates"
            element={
              <AuthGuard>
                <Templates />
              </AuthGuard>
            }
          />
          <Route
            path="/history"
            element={
              <AuthGuard>
                <History />
              </AuthGuard>
            }
          />
          <Route
            path="/settings"
            element={
              <AuthGuard>
                <Settings />
              </AuthGuard>
            }
          />
          <Route
            path="/cases"
            element={
              <AuthGuard>
                <CasesPage />
              </AuthGuard>
            }
          />
          <Route
            path="/cases/:caseId"
            element={
              <AuthGuard>
                <CaseDetailPage />
              </AuthGuard>
            }
          />
          <Route
            path="/calendario"
            element={
              <AuthGuard>
                <CalendarPage />
              </AuthGuard>
            }
          />
          <Route
            path="/reportes"
            element={
              <AuthGuard>
                <ReportsPage />
              </AuthGuard>
            }
          />
          <Route
            path="/uif"
            element={
              <AuthGuard>
                <UIFPage />
              </AuthGuard>
            }
          />
          <Route
            path="/whatsapp"
            element={
              <AuthGuard>
                <WhatsAppPage />
              </AuthGuard>
            }
          />

          {/* Fallback route - redirect to login */}
          <Route path="*" element={<Login />} />
        </Routes>
      </Suspense>
    </>
  );
}

export default App;
