import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';

/**
 * Hook para conexión WebSocket a actualizaciones en tiempo real.
 */
export function useWebSocket(sensorIds = []) {
  const dispatch = useDispatch();
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!sensorIds.length) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    const token = localStorage.getItem('access_token');
    const ws = new WebSocket(`${wsUrl}/sensors?token=${token}`);

    ws.onopen = () => {
      setConnected(true);
      sensorIds.forEach((id) => {
        ws.send(JSON.stringify({ type: 'subscribe', sensor_id: id }));
      });
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      dispatch({
        type: 'sensors/sensorUpdated',
        payload: {
          id: message.sensor_id,
          last_reading: message.reading,
        },
      });
    };

    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    return () => ws.close();
  }, [sensorIds, dispatch]);

  return { connected };
}
