/**
 * EchoSmart Demo — Alert Manager
 *
 * Generates realistic greenhouse alerts based on sensor state.
 */

/** @typedef {{ id: number, severity: string, title: string, zone: string, sensor: string, time: Date, acknowledged: boolean }} Alert */

let _nextId = 1;

const ALERT_TEMPLATES = [
  { severity: "critical", title: "Temperatura alta detectada: {v}",   sensor: "temperature", check: (v) => v > 30 },
  { severity: "critical", title: "Temperatura baja detectada: {v}",   sensor: "temperature", check: (v) => v < 12 },
  { severity: "high",     title: "Humedad de suelo baja: {v}",        sensor: "soil",        check: (v) => v < 40 },
  { severity: "high",     title: "CO₂ elevado: {v}",                  sensor: "co2",         check: (v) => v > 950 },
  { severity: "medium",   title: "Humedad ambiente baja: {v}",        sensor: "humidity",    check: (v) => v < 50 },
  { severity: "medium",   title: "Luminosidad baja: {v}",             sensor: "light",       check: (v) => v < 5000 },
  { severity: "low",      title: "Actualización de firmware disponible", sensor: "gateway",  check: () => false },
  { severity: "low",      title: "Sensor offline detectado",          sensor: "satellite",   check: () => false },
];

const ZONES = ["Zona A", "Zona B", "Zona C"];

/**
 * Create the initial set of demo alerts.
 * @returns {Alert[]}
 */
export function createInitialAlerts() {
  const now = Date.now();
  return [
    _make("critical", "Temperatura alta detectada: 32.1°C", "DS18B20 #2", "Zona A", now - 12 * 60000),
    _make("high",     "Humedad de suelo baja: 38%",         "Soil #1",    "Zona B", now - 28 * 60000),
    _make("medium",   "CO₂ elevado: 980 ppm",               "MH-Z19C",   "Zona A", now - 60 * 60000),
    _make("low",      "Luminosidad baja: 4,200 lux",        "BH1750",    "Zona C", now - 90 * 60000),
  ];
}

/**
 * Evaluate sensors and possibly push a new alert.
 * @param {import("./sensors.js").SensorState[]} sensors
 * @param {Alert[]} alerts
 */
export function evaluateAlerts(sensors, alerts) {
  for (const tpl of ALERT_TEMPLATES) {
    const s = sensors[tpl.sensor];
    if (!s) continue;
    if (tpl.check(s.value)) {
      const duplicate = alerts.find(
        (a) => a.sensor === tpl.sensor && a.severity === tpl.severity && !a.acknowledged
      );
      if (!duplicate) {
        const formatted = tpl.title.replace("{v}", s.value.toFixed(s.spec.decimals) + s.spec.unit);
        const zone = ZONES[Math.floor(Math.random() * ZONES.length)];
        alerts.unshift(_make(tpl.severity, formatted, tpl.sensor, zone, Date.now()));
        if (alerts.length > 20) alerts.pop();
      }
    }
  }
}

/**
 * Format relative time string.
 * @param {Date} date
 * @returns {string}
 */
export function timeAgo(date) {
  const diff = Date.now() - date;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "ahora";
  if (mins < 60) return `hace ${mins} min`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `hace ${hrs}h`;
  return `hace ${Math.floor(hrs / 24)}d`;
}

/**
 * Count active (unacknowledged) alerts.
 */
export function activeCount(alerts) {
  return alerts.filter((a) => !a.acknowledged).length;
}

function _make(severity, title, sensor, zone, ts) {
  return {
    id: _nextId++,
    severity,
    title,
    zone,
    sensor,
    time: new Date(ts),
    acknowledged: false,
  };
}
