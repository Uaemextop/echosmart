import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { fetchSensors, setSelectedSensor } from '../../store/sensorsSlice';
import SensorCard from './SensorCard';
import LoadingSpinner from '../Common/LoadingSpinner';

function SensorGrid() {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const { items, loading, error, filters } = useSelector((state) => state.sensors);

  useEffect(() => {
    dispatch(fetchSensors());
  }, [dispatch]);

  const filteredSensors = items.filter((sensor) => {
    if (filters.gatewayId && sensor.gateway_id !== filters.gatewayId) return false;
    if (filters.type && sensor.type !== filters.type) return false;
    if (filters.search) {
      const search = filters.search.toLowerCase();
      return (
        sensor.name.toLowerCase().includes(search) ||
        sensor.location?.toLowerCase().includes(search)
      );
    }
    return true;
  });

  const handleSelect = (sensor) => {
    dispatch(setSelectedSensor(sensor));
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div>
      <h2 style={{ marginBottom: '16px' }}>{t('sensors.title')}</h2>
      <div className="grid grid-2">
        {filteredSensors.map((sensor) => (
          <SensorCard key={sensor.id} sensor={sensor} onSelect={handleSelect} />
        ))}
      </div>
      {filteredSensors.length === 0 && (
        <p style={{ textAlign: 'center', color: '#64748b', padding: '40px' }}>
          No sensors found
        </p>
      )}
    </div>
  );
}

export default SensorGrid;
