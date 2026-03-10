import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getGateways, deleteGateway } from '../../api/endpoints';
import LoadingSpinner from '../Common/LoadingSpinner';

function GatewayManager() {
  const { t } = useTranslation();
  const [gateways, setGateways] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadGateways = async () => {
      try {
        const response = await getGateways();
        setGateways(response.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load gateways');
      } finally {
        setLoading(false);
      }
    };
    loadGateways();
  }, []);

  const handleDelete = async (id) => {
    try {
      await deleteGateway(id);
      setGateways(gateways.filter((g) => g.id !== id));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete gateway');
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>{t('dashboard.gateways')}</h2>
        <button className="btn btn-primary">Add Gateway</button>
      </div>

      <div className="card table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>{t('sensors.location')}</th>
              <th>{t('sensors.status')}</th>
              <th>Sensors</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {gateways.map((gw) => (
              <tr key={gw.id}>
                <td style={{ fontWeight: 500 }}>{gw.name}</td>
                <td>{gw.location}</td>
                <td>
                  <span className={`badge ${gw.status === 'online' ? 'badge-online' : 'badge-offline'}`}>
                    {gw.status}
                  </span>
                </td>
                <td>{gw.sensor_count || 0}</td>
                <td>
                  <button
                    className="btn btn-danger"
                    style={{ padding: '4px 12px', fontSize: '12px' }}
                    onClick={() => handleDelete(gw.id)}
                  >
                    {t('common.delete')}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {gateways.length === 0 && (
          <p style={{ textAlign: 'center', color: '#64748b', padding: '40px' }}>
            No gateways found
          </p>
        )}
      </div>
    </div>
  );
}

export default GatewayManager;
