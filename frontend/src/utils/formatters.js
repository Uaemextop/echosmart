/**
 * Funciones de formato para valores de sensores.
 */
export function formatTemperature(value) {
  return `${value.toFixed(1)}°C`;
}

export function formatHumidity(value) {
  return `${value.toFixed(1)}%`;
}

export function formatLight(value) {
  return `${Math.round(value)} lux`;
}

export function formatCO2(value) {
  return `${Math.round(value)} ppm`;
}

export function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString('es-MX');
}
