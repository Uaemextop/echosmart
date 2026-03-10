import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';

function QuickStats() {
  const { t } = useTranslation();
  const sensors = useSelector((state) => state.sensors.items);
  const alerts = useSelector((state) => state.alerts.items);

  const totalSensors = sensors.length;
  const onlineSensors = sensors.filter((s) => s.status === 'online').length;
  const activeAlerts = alerts.filter((a) => !a.is_acknowledged).length;
  const gateways = [...new Set(sensors.map((s) => s.gateway_id).filter(Boolean))].length;

  const stats = [
    { label: t('dashboard.total_sensors'), value: totalSensors, color: '#2563eb' },
    { label: t('dashboard.sensors_online'), value: onlineSensors, color: '#10b981' },
    { label: t('dashboard.active_alerts'), value: activeAlerts, color: '#ef4444' },
    { label: t('dashboard.gateways'), value: gateways, color: '#8b5cf6' },
  ];

  return (
    <div className="stats-grid" data-testid="quick-stats">
      {stats.map((stat) => (
        <div className="stat-card" key={stat.label}>
          <div className="stat-value" style={{ color: stat.color }}>
            {stat.value}
          </div>
          <div className="stat-label">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}

export default QuickStats;
