import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// User pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Sensors = lazy(() => import('./pages/Sensors'));
const Alerts = lazy(() => import('./pages/Alerts'));
const Reports = lazy(() => import('./pages/Reports'));

// Admin pages
const AdminLogin = lazy(() => import('./pages/admin/AdminLogin'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const SerialCodes = lazy(() => import('./pages/admin/SerialCodes'));
const EchoPyManagement = lazy(() => import('./pages/admin/EchoPyManagement'));
const UpdateManagement = lazy(() => import('./pages/admin/UpdateManagement'));
const Sales = lazy(() => import('./pages/admin/Sales'));
const ServerConfig = lazy(() => import('./pages/admin/ServerConfig'));

function App() {
  return (
    <Suspense fallback={<div className="loading">Cargando...</div>}>
      <Routes>
        {/* User routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/sensors" element={<Sensors />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/reports" element={<Reports />} />

        {/* Admin routes */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/serials" element={<SerialCodes />} />
        <Route path="/admin/echopy" element={<EchoPyManagement />} />
        <Route path="/admin/updates" element={<UpdateManagement />} />
        <Route path="/admin/sales" element={<Sales />} />
        <Route path="/admin/config" element={<ServerConfig />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

export default App;
