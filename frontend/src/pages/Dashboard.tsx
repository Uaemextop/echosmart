import { useEffect, useState } from 'react';
import { sensorApi, alertApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import type { Sensor, AlertHistory } from '../types';

interface SummaryCard {
  label: string;
  value: number;
  color: string;
}

export default function Dashboard() {
  const { user } = useAuthStore();
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [alerts, setAlerts] = useState<AlertHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const [s, a] = await Promise.all([sensorApi.list(), alertApi.list()]);
        setSensors(Array.isArray(s) ? s : []);
        setAlerts(Array.isArray(a) ? a : []);
      } catch {
        // ignore
      }
      setIsLoading(false);
    }
    load();
  }, []);

  const onlineSensors = sensors.filter((s) => s.status === 'online').length;
  const activeAlerts = alerts.filter((a) => !a.acknowledged).length;

  const cards: SummaryCard[] = [
    { label: 'Total Sensors', value: sensors.length, color: 'bg-blue-50 text-blue-700' },
    { label: 'Online Sensors', value: onlineSensors, color: 'bg-green-50 text-green-700' },
    { label: 'Active Alerts', value: activeAlerts, color: 'bg-red-50 text-red-700' },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p className="text-gray-500">Welcome back, {user?.email}</p>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {cards.map((c) => (
            <div key={c.label} className={`rounded-xl p-5 ${c.color}`}>
              <p className="text-sm font-medium opacity-70">{c.label}</p>
              <p className="text-3xl font-bold mt-1">{c.value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-lg font-semibold mb-4">Sensor Status</h2>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-8 bg-gray-100 rounded animate-pulse" />
              ))}
            </div>
          ) : sensors.length === 0 ? (
            <p className="text-gray-400 text-sm">No sensors registered yet.</p>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {sensors.slice(0, 8).map((s) => (
                <div key={s.id} className="flex items-center gap-2 p-2 rounded-lg border border-gray-100">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      s.status === 'online' ? 'bg-green-500' : s.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                    }`}
                  />
                  <span className="text-sm text-gray-700 truncate">{s.uuid.slice(0, 12)}…</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-8 bg-gray-100 rounded animate-pulse" />
              ))}
            </div>
          ) : alerts.length === 0 ? (
            <p className="text-gray-400 text-sm">No alerts recorded.</p>
          ) : (
            <div className="overflow-auto max-h-56">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-400 border-b">
                    <th className="text-left py-1">Severity</th>
                    <th className="text-left py-1">Message</th>
                    <th className="text-left py-1">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.slice(0, 10).map((a) => (
                    <tr key={a.id} className="border-b border-gray-50">
                      <td className="py-1.5">
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            a.severity === 'critical'
                              ? 'bg-red-100 text-red-700'
                              : a.severity === 'warning'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {a.severity}
                        </span>
                      </td>
                      <td className="py-1.5 text-gray-600 max-w-[160px] truncate">{a.message}</td>
                      <td className="py-1.5 text-gray-400 whitespace-nowrap">
                        {new Date(a.triggeredAt).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
