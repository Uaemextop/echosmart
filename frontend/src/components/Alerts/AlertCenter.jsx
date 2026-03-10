import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { fetchAlerts, acknowledgeAlert } from '../../store/alertsSlice';
import { formatDate } from '../../utils/format';
import LoadingSpinner from '../Common/LoadingSpinner';

function AlertCenter() {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const { items, loading, error } = useSelector((state) => state.alerts);
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    dispatch(fetchAlerts());
  }, [dispatch]);

  const filteredAlerts = severityFilter === 'all'
    ? items
    : items.filter((a) => a.severity === severityFilter);

  const handleAcknowledge = (id) => {
    dispatch(acknowledgeAlert(id));
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>{t('alerts.title')}</h2>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}
        >
          <option value="all">{t('common.filter')}</option>
          <option value="critical">{t('alerts.critical')}</option>
          <option value="high">{t('alerts.high')}</option>
          <option value="medium">{t('alerts.medium')}</option>
          <option value="low">{t('alerts.low')}</option>
        </select>
      </div>

      {filteredAlerts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: '#64748b' }}>{t('alerts.no_alerts')}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredAlerts.map((alert) => (
            <div key={alert.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className={`badge badge-${alert.severity}`}>
                  {t(`alerts.${alert.severity}`)}
                </span>
                <div>
                  <p style={{ fontWeight: 500 }}>{alert.message}</p>
                  <p style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {formatDate(alert.created_at)}
                  </p>
                </div>
              </div>
              {!alert.is_acknowledged && (
                <button
                  className="btn btn-secondary"
                  onClick={() => handleAcknowledge(alert.id)}
                >
                  {t('alerts.acknowledge')}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlertCenter;
