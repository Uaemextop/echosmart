import { useEffect, useRef, useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addReading } from '../store/readingsSlice';
import { addAlert } from '../store/alertsSlice';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080/ws';
const MAX_RECONNECT_DELAY_MS = 30000;

export const useWebSocket = (sensorIds = []) => {
  const dispatch = useDispatch();
  const { token } = useSelector((state) => state.auth);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptRef = useRef(0);

  const connect = useCallback(() => {
    if (!token || sensorIds.length === 0) return;

    try {
      const ws = new WebSocket(`${WS_URL}?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectAttemptRef.current = 0;
        ws.send(JSON.stringify({ type: 'subscribe', sensor_ids: sensorIds }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'sensor_update') {
            dispatch(addReading(message.payload));
          } else if (message.type === 'alert') {
            dispatch(addAlert(message.payload));
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        setConnected(false);
        const delay = Math.min(
          1000 * Math.pow(2, reconnectAttemptRef.current),
          MAX_RECONNECT_DELAY_MS
        );
        reconnectAttemptRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // connection failed, will retry via onclose
    }
  }, [token, sensorIds, dispatch]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { connected };
};

export default useWebSocket;
