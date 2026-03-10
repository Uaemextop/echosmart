import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { getSeverityColor } from '../../theme';

function AlertBanner() {
  const { t } = useTranslation();
  const alerts = useSelector((state) => state.alerts.items);
  const unacknowledged = alerts.filter((a) => !a.is_acknowledged);
  const critical = unacknowledged.filter((a) => a.severity === 'critical');

  if (critical.length === 0) return null;

  return (
    <div
      style={{
        background: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: '8px',
        padding: '12px 20px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
    >
      <span style={{ fontSize: '20px' }}>⚠️</span>
      <div>
        <strong style={{ color: getSeverityColor('critical') }}>
          {critical.length} {t('alerts.critical')} {t('alerts.title').toLowerCase()}
        </strong>
        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
          {critical[0]?.message}
        </p>
      </div>
    </div>
  );
}

export default AlertBanner;
