import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
  LayoutDashboard,
  Cpu,
  Bell,
  Users,
  Activity,
  Menu,
  X,
  Leaf,
} from 'lucide-react';
import clsx from 'clsx';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
  superadminOnly?: boolean;
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
  { to: '/sensors', label: 'Sensors', icon: <Cpu size={18} /> },
  { to: '/sensors/alerts', label: 'Alert Rules', icon: <Bell size={18} /> },
  { to: '/admin/tenants', label: 'Tenants', icon: <Users size={18} />, superadminOnly: true },
  { to: '/admin/health', label: 'System Health', icon: <Activity size={18} />, superadminOnly: true },
];

export default function Sidebar() {
  const { user } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);

  const filtered = navItems.filter((item) => !item.superadminOnly || user?.role === 'superadmin');

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    clsx(
      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
      isActive ? 'bg-green-100 text-green-800' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
    );

  const nav = (
    <nav className="p-4 space-y-1">
      {filtered.map((item) => (
        <NavLink key={item.to} to={item.to} className={linkClass} onClick={() => setIsOpen(false)}>
          {item.icon}
          {item.label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow border border-gray-200"
        onClick={() => setIsOpen((o) => !o)}
        aria-label="Toggle menu"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile overlay */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 bg-black/30 z-40" onClick={() => setIsOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed md:static inset-y-0 left-0 z-50 w-56 bg-white border-r border-gray-200 flex flex-col transition-transform duration-200',
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div className="flex items-center gap-2 px-4 py-5 border-b border-gray-100">
          <Leaf size={22} className="text-green-500" />
          <span className="text-lg font-bold text-gray-900">EchoSmart</span>
        </div>
        {nav}
      </aside>
    </>
  );
}
