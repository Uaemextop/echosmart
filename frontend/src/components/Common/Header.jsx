import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { toggleSidebar, toggleTheme } from '../../store/uiSlice';
import useAuth from '../../hooks/useAuth';

function Header() {
  const dispatch = useDispatch();
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const { theme } = useSelector((state) => state.ui);

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'es' : 'en';
    i18n.changeLanguage(newLang);
  };

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: 'var(--header-height)',
        background: 'white',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        zIndex: 100,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={() => dispatch(toggleSidebar())}
          style={{ background: 'none', fontSize: '20px', padding: '4px' }}
          aria-label="Toggle sidebar"
        >
          ☰
        </button>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--primary)' }}>
          {t('app.title')}
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={toggleLanguage}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '13px' }}
        >
          {i18n.language === 'en' ? '🇪🇸 ES' : '🇺🇸 EN'}
        </button>
        <button
          onClick={() => dispatch(toggleTheme())}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '13px' }}
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        {user && (
          <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
            {user.full_name || user.email}
          </span>
        )}
        <button
          onClick={logout}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '13px' }}
        >
          {t('auth.logout')}
        </button>
      </div>
    </header>
  );
}

export default Header;
