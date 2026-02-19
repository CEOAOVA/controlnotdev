import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ProcessPage } from './pages/ProcessPage';
import { Dashboard } from './pages/Dashboard';
import { Templates } from './pages/Templates';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';
import { CasesPage } from './pages/CasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { CalendarPage } from './pages/CalendarPage';
import { ReportsPage } from './pages/ReportsPage';
import { UIFPage } from './pages/UIFPage';
import { WhatsAppPage } from './pages/WhatsAppPage';
import { AuthGuard } from './components/auth/AuthGuard';

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
    </>
  );
}

export default App;
