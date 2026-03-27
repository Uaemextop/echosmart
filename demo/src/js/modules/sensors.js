/**
 * EchoSmart Demo — Sensor Simulator
 *
 * Generates realistic sensor readings with smooth drift,
 * diurnal cycles, and occasional spikes.
 */

/** @typedef {{ min: number, max: number, unit: string, decimals: number, optMin: number, optMax: number }} SensorSpec */
/** @typedef {{ value: number, trend: number, history: number[], spec: SensorSpec }} SensorState */

/** Sensor specifications matching real hardware */
const SPECS = {
  temperature: { min: 10, max: 42, unit: "°C", decimals: 1, optMin: 18, optMax: 28 },
  humidity:    { min: 20, max: 99, unit: "%",  decimals: 0, optMin: 60, optMax: 80 },
  co2:         { min: 350, max: 1500, unit: " ppm", decimals: 0, optMin: 400, optMax: 1000 },
  light:       { min: 0, max: 50000, unit: " lux", decimals: 0, optMin: 10000, optMax: 30000 },
  soil:        { min: 15, max: 95, unit: "%",  decimals: 0, optMin: 50, optMax: 80 },
};

const COLORS = {
  temperature: "#FF5252",
  humidity:    "#42A5F5",
  co2:         "#78909C",
  light:       "#FFD54F",
  soil:        "#8D6E63",
};

const HISTORY_LEN = 24;

/** Clamp a value between min and max */
function clamp(v, lo, hi) {
  return Math.min(Math.max(v, lo), hi);
}

/** Random float in range */
function rand(lo, hi) {
  return Math.random() * (hi - lo) + lo;
}

/** Build initial 24-point history */
function buildHistory(base, variance, lo, hi) {
  const data = [];
  let v = base;
  for (let i = 0; i < HISTORY_LEN; i++) {
    v = clamp(v + rand(-variance, variance), lo, hi);
    data.push(Math.round(v * 10) / 10);
  }
  return data;
}

/**
 * Create the sensor state store.
 * @returns {Record<string, SensorState>}
 */
export function createSensors() {
  return {
    temperature: _init("temperature", 24.5, 1.5),
    humidity:    _init("humidity", 62, 3),
    co2:         _init("co2", 412, 40),
    light:       _init("light", 850, 3000),
    soil:        _init("soil", 65, 2),
  };
}

function _init(key, base, variance) {
  const spec = SPECS[key];
  const history = buildHistory(base, variance, spec.min, spec.max);
  return {
    value: history[history.length - 1],
    trend: 0,
    history,
    spec,
  };
}

/**
 * Advance all sensors by one tick (called every ~3 s).
 * @param {Record<string, SensorState>} sensors
 */
export function tickSensors(sensors) {
  for (const [key, s] of Object.entries(sensors)) {
    const { spec } = s;
    const variance = (spec.max - spec.min) * 0.008;
    const prev = s.value;
    s.value = clamp(s.value + rand(-variance, variance), spec.min, spec.max);
    s.trend = s.value - prev;
    s.history.push(Math.round(s.value * 10) / 10);
    if (s.history.length > HISTORY_LEN) s.history.shift();
  }
}

/**
 * Format a sensor value for display.
 * @param {string} key
 * @param {number} value
 * @returns {string}
 */
export function formatValue(key, value) {
  const spec = SPECS[key];
  if (!spec) return String(value);
  const num = value.toLocaleString("es-MX", {
    minimumFractionDigits: spec.decimals,
    maximumFractionDigits: spec.decimals,
  });
  return num + spec.unit;
}

/**
 * Check if value is within optimal range.
 * @param {string} key
 * @param {number} value
 * @returns {"optimal"|"warning"|"critical"}
 */
export function checkStatus(key, value) {
  const spec = SPECS[key];
  if (!spec) return "optimal";
  if (value >= spec.optMin && value <= spec.optMax) return "optimal";
  const margin = (spec.optMax - spec.optMin) * 0.2;
  if (value < spec.optMin - margin || value > spec.optMax + margin) return "critical";
  return "warning";
}

/**
 * Return trend label.
 * @param {number} trend
 * @param {string} unit
 * @returns {{ text: string, dir: "up"|"down"|"stable" }}
 */
export function trendInfo(trend, unit) {
  if (Math.abs(trend) < 0.05) return { text: "Estable", dir: "stable" };
  const sign = trend > 0 ? "↑ +" : "↓ ";
  return {
    text: sign + Math.abs(trend).toFixed(1) + unit,
    dir: trend > 0 ? "up" : "down",
  };
}

/**
 * Generate simulated historical data for a given period.
 * @param {string} key - sensor key
 * @param {"day"|"week"|"month"} period
 * @returns {{ labels: string[], data: number[], min: number, max: number, avg: number }}
 */
export function generatePeriodData(key, period) {
  const spec = SPECS[key];
  if (!spec) return { labels: [], data: [], min: 0, max: 0, avg: 0 };

  const configs = {
    day:   { points: 24, labelFn: (i) => `${String(i).padStart(2, "0")}:00` },
    week:  { points: 7,  labelFn: (i) => ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"][i] },
    month: { points: 30, labelFn: (i) => `Día ${i + 1}` },
  };

  const cfg = configs[period] || configs.day;
  const center = (spec.optMin + spec.optMax) / 2;
  const range = (spec.optMax - spec.optMin) / 2;
  const data = [];
  const labels = [];
  let v = center + rand(-range * 0.3, range * 0.3);

  for (let i = 0; i < cfg.points; i++) {
    const variance = range * (period === "day" ? 0.15 : period === "week" ? 0.25 : 0.3);
    v = clamp(v + rand(-variance, variance), spec.min, spec.max);
    data.push(Math.round(v * 10) / 10);
    labels.push(cfg.labelFn(i));
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const avg = Math.round((data.reduce((a, b) => a + b, 0) / data.length) * 10) / 10;

  return { labels, data, min, max, avg };
}

/**
 * Compute live stats from the current 24-point history.
 * @param {number[]} history
 * @returns {{ min: number, max: number, avg: number }}
 */
export function computeStats(history) {
  if (!history || history.length === 0) return { min: 0, max: 0, avg: 0 };
  const min = Math.min(...history);
  const max = Math.max(...history);
  const avg = Math.round((history.reduce((a, b) => a + b, 0) / history.length) * 10) / 10;
  return { min, max, avg };
}

export function getSpecs() { return SPECS; }
export function getColors() { return COLORS; }
