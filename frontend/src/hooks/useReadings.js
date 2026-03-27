import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

/**
 * Hook para fetching y caching de lecturas de sensores.
 */
export function useReadings(sensorId, { from, to, refreshInterval = 60000 } = {}) {
  const dispatch = useDispatch();
  const readings = useSelector((state) => state.sensors.byId[sensorId]?.readings || []);
  const loading = useSelector((state) => state.sensors.loading);
  const error = useSelector((state) => state.sensors.error);

  useEffect(() => {
    if (!sensorId) return;

    // TODO: Implementar fetch de lecturas con refresh periódico

    return () => {
      // Cleanup
    };
  }, [sensorId, from, to, refreshInterval, dispatch]);

  return { readings, loading, error };
}
