import { useEffect, useState } from 'react';

interface LogEntry {
  id: number;
  level: 'info' | 'warn' | 'error';
  message: string;
  time: string;
}

const mockLogs: LogEntry[] = [
  { id: 1, level: 'info', message: 'Gateway gateway-001 connected', time: '10:00:01' },
  { id: 2, level: 'info', message: 'Sensor abc-123 registered via SSDP', time: '10:00:15' },
  { id: 3, level: 'warn', message: 'Sensor xyz-789 missed heartbeat', time: '10:01:00' },
  { id: 4, level: 'error', message: 'PostgreSQL pool error: timeout', time: '10:02:30' },
  { id: 5, level: 'info', message: 'Email queue processed 3 jobs', time: '10:03:00' },
];

interface Metric {
  label: string;
  value: string;
  color: string;
}

export default function SystemHealth() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>(mockLogs);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 30000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    setMetrics([
      { label: 'CPU Usage', value: `${(20 + Math.random() * 30).toFixed(1)}%`, color: 'text-blue-600' },
      { label: 'Memory Usage', value: `${(40 + Math.random() * 30).toFixed(1)}%`, color: 'text-purple-600' },
      { label: 'DB Connections', value: `${Math.floor(3 + Math.random() * 7)}/20`, color: 'text-green-600' },
      { label: 'MQTT Clients', value: `${Math.floor(2 + Math.random() * 5)}`, color: 'text-yellow-600' },
    ]);
  }, [tick]);

  const levelClass = (level: LogEntry['level']) =>
    level === 'error'
      ? 'bg-red-100 text-red-700'
      : level === 'warn'
      ? 'bg-yellow-100 text-yellow-700'
      : 'bg-blue-100 text-blue-700';

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">System Health</h1>
        <span className="text-xs text-gray-400">Auto-refreshes every 30s</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div key={m.label} className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-sm text-gray-500">{m.label}</p>
            <p className={`text-2xl font-bold mt-1 ${m.color}`}>{m.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-lg font-semibold mb-4">Gateway Status</h2>
          <div className="space-y-3">
            {[{ id: 'gateway-001', status: 'online' }, { id: 'gateway-002', status: 'offline' }].map((gw) => (
              <div key={gw.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">{gw.id}</span>
                <span
                  className={`flex items-center gap-1.5 text-xs font-medium ${
                    gw.status === 'online' ? 'text-green-600' : 'text-gray-400'
                  }`}
                >
                  <span
                    className={`w-2 h-2 rounded-full ${gw.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}
                  />
                  {gw.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-lg font-semibold mb-4">Recent System Logs</h2>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {logs.map((log) => (
              <div key={log.id} className="flex items-start gap-2 text-sm">
                <span className={`px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap ${levelClass(log.level)}`}>
                  {log.level}
                </span>
                <span className="text-gray-600 flex-1">{log.message}</span>
                <span className="text-gray-400 text-xs whitespace-nowrap">{log.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-400 text-right">Tick #{tick} – metrics are simulated</p>
    </div>
  );
}
