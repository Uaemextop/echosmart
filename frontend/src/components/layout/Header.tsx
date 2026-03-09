import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Bell, ChevronDown, LogOut, User } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { useTenantStore } from '../../store/tenantStore';

const routeTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/sensors': 'Sensors',
  '/sensors/alerts': 'Alert Rules',
  '/admin/tenants': 'Tenants',
  '/admin/tenants/create': 'Create Tenant',
  '/admin/health': 'System Health',
};

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { currentTenant } = useTenantStore();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const title = routeTitles[location.pathname] || 'EchoSmart';

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 md:px-6">
      <h2 className="text-base font-semibold text-gray-800">{title}</h2>

      <div className="flex items-center gap-3">
        {currentTenant?.settings?.logoUrl ? (
          <img src={currentTenant.settings.logoUrl} alt="logo" className="h-6" />
        ) : currentTenant ? (
          <span className="text-sm text-gray-500">{currentTenant.name}</span>
        ) : null}

        <button className="relative p-2 text-gray-500 hover:text-gray-700">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        <div className="relative">
          <button
            onClick={() => setDropdownOpen((o) => !o)}
            className="flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900"
          >
            <div className="w-7 h-7 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-medium text-xs">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <span className="hidden sm:block">{user?.email}</span>
            <ChevronDown size={14} />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-44 bg-white border border-gray-200 rounded-xl shadow-lg z-10 py-1">
              <button
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                onClick={() => { setDropdownOpen(false); navigate('/profile'); }}
              >
                <User size={14} /> Profile
              </button>
              <hr className="my-1 border-gray-100" />
              <button
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-500 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut size={14} /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
