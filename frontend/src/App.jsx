import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import DashboardLayout from './components/Dashboard/DashboardLayout';
import SensorGrid from './components/Dashboard/SensorGrid';
import QuickStats from './components/Dashboard/QuickStats';
import SensorList from './components/Sensors/SensorList';
import AlertCenter from './components/Alerts/AlertCenter';
import ReportList from './components/Reports/ReportList';
import LoginForm from './components/Auth/LoginForm';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import UserManagement from './components/Admin/UserManagement';
import GatewayManager from './components/Admin/GatewayManager';
import ErrorBoundary from './components/Common/ErrorBoundary';

function DashboardHome() {
  return (
    <>
      <QuickStats />
      <SensorGrid />
    </>
  );
}

function App() {
  const { isAuthenticated } = useSelector((state) => state.auth);

  return (
    <ErrorBoundary>
      <div className="app-container">
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginForm />
            }
          />
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard" element={<DashboardHome />} />
              <Route path="/sensors" element={<SensorList />} />
              <Route path="/sensors/:id" element={<SensorList />} />
              <Route path="/alerts" element={<AlertCenter />} />
              <Route path="/reports" element={<ReportList />} />
              <Route path="/admin/users" element={<UserManagement />} />
              <Route path="/admin/gateways" element={<GatewayManager />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
        </Routes>
      </div>
    </ErrorBoundary>
  );
}

export default App;
