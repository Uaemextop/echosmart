import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { formatTime, formatNumber } from '../../utils/format';

function TemperatureChart({ data = [], title = 'Sensor Readings' }) {
  const chartData = data.map((item) => ({
    ...item,
    time: formatTime(item.timestamp),
    displayValue: Number(item.value),
  }));

  return (
    <div className="card" style={{ padding: '20px' }}>
      <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>{title}</h3>
      {chartData.length === 0 ? (
        <p style={{ textAlign: 'center', color: '#64748b', padding: '40px 0' }}>
          No data available
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              stroke="#94a3b8"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#94a3b8"
              tickFormatter={(val) => formatNumber(val)}
            />
            <Tooltip
              contentStyle={{
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
              }}
              formatter={(value) => [formatNumber(value), 'Value']}
            />
            <Line
              type="monotone"
              dataKey="displayValue"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default TemperatureChart;
