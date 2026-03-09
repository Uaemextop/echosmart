import { useState } from 'react';

interface SensorPoint {
  id: string;
  label: string;
  x: number;
  y: number;
  value: number;
}

interface Props {
  sensors: SensorPoint[];
}

function tempToColor(value: number): string {
  // cold (blue) <15 -> ideal (green) 18-25 -> hot (red) >30
  if (value < 15) return 'rgb(59,130,246)';
  if (value < 18) return `rgb(${Math.round(59 + (value - 15) * 60)},${Math.round(130 + (value - 15) * 20)},${Math.round(246 - (value - 15) * 60)})`;
  if (value <= 25) return `rgb(${Math.round(34 + (value - 18) * 15)},${Math.round(197 - (value - 18) * 8)},${Math.round(94 - (value - 18) * 5)})`;
  if (value <= 30) return `rgb(${Math.round(245 + (value - 25) * 2)},${Math.round(158 - (value - 25) * 20)},${Math.round(11 - (value - 25))})`;
  return 'rgb(239,68,68)';
}

export default function SensorHeatmap({ sensors }: Props) {
  const [tooltip, setTooltip] = useState<{ label: string; value: number; x: number; y: number } | null>(null);

  return (
    <div className="space-y-3">
      <div className="relative bg-gray-50 rounded-xl overflow-hidden" style={{ height: 200 }}>
        {sensors.map((s) => (
          <div
            key={s.id}
            onMouseEnter={() => setTooltip({ label: s.label, value: s.value, x: s.x, y: s.y })}
            onMouseLeave={() => setTooltip(null)}
            style={{
              position: 'absolute',
              left: `${s.x}%`,
              top: `${s.y}%`,
              width: '20%',
              height: '20%',
              backgroundColor: tempToColor(s.value),
              opacity: 0.8,
              borderRadius: 8,
              cursor: 'pointer',
              transition: 'opacity 0.2s',
            }}
          />
        ))}
        {tooltip && (
          <div
            className="absolute bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs shadow-lg pointer-events-none z-10"
            style={{ left: `${tooltip.x + 22}%`, top: `${tooltip.y}%` }}
          >
            <p className="font-medium">{tooltip.label}</p>
            <p className="text-gray-500">{tooltip.value.toFixed(1)}°C</p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <span>Cold</span>
        <div
          className="h-3 flex-1 rounded"
          style={{
            background: 'linear-gradient(to right, rgb(59,130,246), rgb(34,197,94), rgb(245,158,11), rgb(239,68,68))',
          }}
        />
        <span>Hot</span>
        <span className="ml-2">({'<'}15°C → {'>'}30°C)</span>
      </div>
    </div>
  );
}
