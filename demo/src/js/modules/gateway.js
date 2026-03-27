/**
 * EchoSmart Demo — Gateway Simulator
 *
 * Simulates 3 gateway devices with uptime, CPU, memory.
 */

const GATEWAYS = [
  { id: "gw-01", name: "Gateway-01", sensors: 3, status: "online",  uptimeMs: 14 * 86400000 + 7 * 3600000 },
  { id: "gw-02", name: "Gateway-02", sensors: 3, status: "online",  uptimeMs: 8 * 86400000 + 2 * 3600000 },
  { id: "gw-03", name: "Gateway-03", sensors: 2, status: "warning", uptimeMs: 1 * 86400000 + 12 * 3600000 },
];

/**
 * Return current gateway state.
 */
export function getGateways() {
  return GATEWAYS.map((gw) => ({
    ...gw,
    cpu: Math.round(15 + Math.random() * 25),
    mem: Math.round(30 + Math.random() * 30),
    uptime: formatUptime(gw.uptimeMs),
  }));
}

/**
 * Tick uptime forward by given ms.
 */
export function tickGateways(ms) {
  for (const gw of GATEWAYS) {
    gw.uptimeMs += ms;
  }
}

function formatUptime(ms) {
  const d = Math.floor(ms / 86400000);
  const h = Math.floor((ms % 86400000) / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  if (d > 0) return `${d}d ${h}h`;
  return `${h}h ${m}m`;
}
