import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { fetchSensors } from '../../store/sensorsSlice';
import { formatDate, formatReadingValue } from '../../utils/format';
import LoadingSpinner from '../Common/LoadingSpinner';

function SensorList() {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const { items, loading, error } = useSelector((state) => state.sensors);

  useEffect(() => {
    dispatch(fetchSensors());
  }, [dispatch]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>{t('sensors.title')}</h2>
        <button className="btn btn-primary">{t('sensors.create')}</button>
      </div>

      <div className="card table-container">
        <table>
          <thead>
            <tr>
              <th>{t('sensors.name')}</th>
              <th>{t('sensors.type')}</th>
              <th>{t('sensors.location')}</th>
              <th>{t('sensors.status')}</th>
              <th>{t('sensors.last_reading')}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((sensor) => (
              <tr key={sensor.id}>
                <td style={{ fontWeight: 500 }}>{sensor.name}</td>
                <td>{sensor.type}</td>
                <td>{sensor.location}</td>
                <td>
                  <span className={`badge ${sensor.status === 'online' ? 'badge-online' : 'badge-offline'}`}>
                    {sensor.status}
                  </span>
                </td>
                <td>
                  {formatReadingValue(sensor.last_reading, sensor.unit)}
                  {sensor.last_reading_at && (
                    <span style={{ display: 'block', fontSize: '12px', color: '#94a3b8' }}>
                      {formatDate(sensor.last_reading_at)}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && (
          <p style={{ textAlign: 'center', color: '#64748b', padding: '40px' }}>
            No sensors found
          </p>
        )}
      </div>
    </div>
  );
}

export default SensorList;
