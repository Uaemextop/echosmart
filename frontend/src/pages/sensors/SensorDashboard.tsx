import { useEffect, useState } from 'react';
import { sensorApi } from '../../services/api';
import type { Sensor, SensorReading } from '../../types';
import TemperatureChart from '../../components/charts/TemperatureChart';
import SensorHeatmap from '../../components/charts/SensorHeatmap';

export default function SensorDashboard() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [chartData, setChartData] = useState<SensorReading[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    sensorApi.list().then((data: Sensor[]) => {
      setSensors(Array.isArray(data) ? data : []);
      if (data.length) setSelectedId(data[0].id);
      setIsLoading(false);
    }).catch(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    sensorApi.getData(selectedId, { field: 'temperature' }).then((res: { data: SensorReading[] }) => {
      setChartData(res.data || []);
    }).catch(() => {});
  }, [selectedId]);

  const selected = sensors.find((s) => s.id === selectedId);

  const stats = chartData.length
    ? {
        min: Math.min(...chartData.map((d) => d.temperature ?? 0)).toFixed(1),
        max: Math.max(...chartData.map((d) => d.temperature ?? 0)).toFixed(1),
        avg: (chartData.reduce((a, d) => a + (d.temperature ?? 0), 0) / chartData.length).toFixed(1),
      }
    : null;

  const heatmapData = sensors.map((s, i) => ({
    id: s.id,
    label: s.uuid.slice(0, 8),
    x: (i % 4) * 25,
    y: Math.floor(i / 4) * 25,
    value: 18 + Math.random() * 15,
  }));

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Sensor Monitoring</h1>
      <div className="flex gap-5">
        <div className="w-56 bg-white rounded-xl border border-gray-200 p-3 space-y-1 shrink-0">
          <p className="text-xs font-medium text-gray-400 px-2 mb-2">SENSORS</p>
          {isLoading
            ? [...Array(4)].map((_, i) => <div key={i} className="h-8 bg-gray-100 rounded animate-pulse" />)
            : sensors.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelectedId(s.id)}
                  className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm text-left transition-colors ${
                    selectedId === s.id ? 'bg-green-50 text-green-700' : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <span
                    className={`w-2 h-2 rounded-full shrink-0 ${
                      s.status === 'online' ? 'bg-green-500' : s.status === 'error' ? 'bg-red-500' : 'bg-gray-300'
                    }`}
                  />
                  <span className="truncate">{s.uuid.slice(0, 10)}</span>
                </button>
              ))}
        </div>

        <div className="flex-1 space-y-5">
          {selected && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="font-semibold text-gray-900">{selected.uuid}</h2>
                  <p className="text-sm text-gray-400">{selected.sensorType} · {selected.gatewayId}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    selected.status === 'online' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {selected.status}
                </span>
              </div>

              {stats && (
                <div className="grid grid-cols-3 gap-3 mb-4">
                  {[{ label: 'Min °C', value: stats.min }, { label: 'Avg °C', value: stats.avg }, { label: 'Max °C', value: stats.max }].map((s) => (
                    <div key={s.label} className="bg-gray-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-400">{s.label}</p>
                      <p className="text-xl font-bold text-gray-800">{s.value}</p>
                    </div>
                  ))}
                </div>
              )}

              <TemperatureChart data={chartData} sensors={[selected.uuid]} height={220} />
            </div>
          )}

          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4">Greenhouse Heatmap</h2>
            <SensorHeatmap sensors={heatmapData} />
          </div>
        </div>
      </div>
    </div>
  );
}
