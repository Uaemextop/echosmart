import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { createSensor, updateSensor } from '../../store/sensorsSlice';

function SensorModal({ sensor = null, onClose }) {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const isEditing = !!sensor;

  const [formData, setFormData] = useState({
    name: sensor?.name || '',
    type: sensor?.type || 'temperature',
    location: sensor?.location || '',
    unit: sensor?.unit || '°C',
    gateway_id: sensor?.gateway_id || '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isEditing) {
      dispatch(updateSensor({ id: sensor.id, data: formData }));
    } else {
      dispatch(createSensor(formData));
    }
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2 style={{ marginBottom: '20px' }}>
          {isEditing ? t('sensors.edit') : t('sensors.create')}
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>{t('sensors.name')}</label>
            <input
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>{t('sensors.type')}</label>
            <select name="type" value={formData.type} onChange={handleChange}>
              <option value="temperature">Temperature</option>
              <option value="humidity">Humidity</option>
              <option value="pressure">Pressure</option>
              <option value="co2">CO2</option>
              <option value="noise">Noise</option>
              <option value="light">Light</option>
            </select>
          </div>
          <div className="form-group">
            <label>{t('sensors.location')}</label>
            <input
              name="location"
              value={formData.location}
              onChange={handleChange}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              {t('common.cancel')}
            </button>
            <button type="submit" className="btn btn-primary">
              {t('common.save')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SensorModal;
