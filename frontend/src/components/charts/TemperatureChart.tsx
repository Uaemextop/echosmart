import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { SensorReading } from '../../types';

const LINE_COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

interface Props {
  data: SensorReading[];
  sensors: string[];
  height?: number;
}

interface TooltipPayload {
  name: string;
  value: number;
  color: string;
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayload[]; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-xs">
      <p className="text-gray-500 mb-2">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <strong>{p.value?.toFixed(2)}°C</strong>
        </p>
      ))}
    </div>
  );
}

export default function TemperatureChart({ data, sensors, height = 250 }: Props) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center text-gray-400 text-sm" style={{ height }}>
        No data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          tickLine={false}
        />
        <YAxis
          unit="°C"
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          tickLine={false}
          axisLine={false}
          width={45}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        {sensors.map((sensor, i) => (
          <Line
            key={sensor}
            type="monotone"
            dataKey="temperature"
            name={sensor.slice(0, 10)}
            stroke={LINE_COLORS[i % LINE_COLORS.length]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
