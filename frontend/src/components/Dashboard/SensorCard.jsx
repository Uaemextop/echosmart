import { useTranslation } from 'react-i18next';
import { getSensorIcon } from '../../theme';
import { formatReadingValue, timeAgo } from '../../utils/format';

function SensorCard({ sensor, onSelect }) {
  const { t } = useTranslation();
  const isOnline = sensor.status === 'online';

  return (
    <div
      className="card sensor-card"
      onClick={() => onSelect && onSelect(sensor)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect && onSelect(sensor)}
      style={{ cursor: 'pointer', transition: 'box-shadow 0.2s' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '28px' }}>{getSensorIcon(sensor.type)}</span>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 600 }}>{sensor.name}</h3>
            <p style={{ fontSize: '13px', color: '#64748b' }}>{sensor.location}</p>
          </div>
        </div>
        <span className={`badge ${isOnline ? 'badge-online' : 'badge-offline'}`}>
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>

      <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <p style={{ fontSize: '13px', color: '#64748b' }}>{t('sensors.last_reading')}</p>
          <p style={{ fontSize: '24px', fontWeight: 700, color: '#2563eb' }}>
            {formatReadingValue(sensor.last_reading, sensor.unit)}
          </p>
        </div>
        {sensor.last_reading_at && (
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>
            {timeAgo(sensor.last_reading_at)}
          </span>
        )}
      </div>
    </div>
  );
}

export default SensorCard;
