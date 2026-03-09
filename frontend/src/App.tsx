import { Navigate, useLocation } from 'react-router-dom';
import { Routes, Route } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { useTenantTheme } from './hooks/useTenantTheme';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import TenantList from './pages/admin/TenantList';
import CreateTenant from './pages/admin/CreateTenant';
import SystemHealth from './pages/admin/SystemHealth';
import SensorDashboard from './pages/sensors/SensorDashboard';
import AlertRules from './pages/sensors/AlertRules';
import type { ReactNode } from 'react';

function AppLayout({ children }: { children: ReactNode }) {
  useTenantTheme();
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}

function ProtectedRoute({ children, roles }: { children: ReactNode; roles?: string[] }) {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <AppLayout>{children}</AppLayout>;
}

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/sensors"
        element={
          <ProtectedRoute>
            <SensorDashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/sensors/alerts"
        element={
          <ProtectedRoute>
            <AlertRules />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/tenants"
        element={
          <ProtectedRoute roles={['superadmin']}>
            <TenantList />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/tenants/create"
        element={
          <ProtectedRoute roles={['superadmin']}>
            <CreateTenant />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/health"
        element={
          <ProtectedRoute roles={['superadmin']}>
            <SystemHealth />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
      <Route path="*" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
    </Routes>
  );
}
