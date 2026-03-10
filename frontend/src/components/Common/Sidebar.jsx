import { NavLink } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';

const navItems = [
  { path: '/dashboard', icon: '📊', labelKey: 'dashboard.title' },
  { path: '/sensors', icon: '📡', labelKey: 'sensors.title' },
  { path: '/alerts', icon: '🔔', labelKey: 'alerts.title' },
  { path: '/reports', icon: '📋', labelKey: 'reports.title' },
];

const adminItems = [
  { path: '/admin/users', icon: '👥', labelKey: 'admin.users' },
  { path: '/admin/gateways', icon: '🌐', labelKey: 'dashboard.gateways' },
];

function Sidebar() {
  const { t } = useTranslation();
  const { sidebarOpen } = useSelector((state) => state.ui);
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.role === 'admin';

  if (!sidebarOpen) return null;

  const linkStyle = (isActive) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '10px 20px',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: isActive ? 600 : 400,
    background: isActive ? '#eff6ff' : 'transparent',
    color: isActive ? '#2563eb' : '#64748b',
    transition: 'all 0.2s',
  });

  return (
    <aside
      style={{
        position: 'fixed',
        top: 'var(--header-height)',
        left: 0,
        bottom: 0,
        width: 'var(--sidebar-width)',
        background: 'white',
        borderRight: '1px solid var(--border)',
        padding: '16px 12px',
        overflowY: 'auto',
        zIndex: 90,
      }}
    >
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => linkStyle(isActive)}
          >
            <span>{item.icon}</span>
            <span>{t(item.labelKey)}</span>
          </NavLink>
        ))}

        {isAdmin && (
          <>
            <div
              style={{
                margin: '16px 0 8px',
                padding: '0 20px',
                fontSize: '11px',
                fontWeight: 600,
                color: '#94a3b8',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Admin
            </div>
            {adminItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                style={({ isActive }) => linkStyle(isActive)}
              >
                <span>{item.icon}</span>
                <span>{t(item.labelKey)}</span>
              </NavLink>
            ))}
          </>
        )}
      </nav>
    </aside>
  );
}

export default Sidebar;
