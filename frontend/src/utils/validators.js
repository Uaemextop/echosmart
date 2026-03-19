/**
 * Funciones de validación.
 */
export function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

export function isInRange(value, min, max) {
  return value >= min && value <= max;
}

export function isOptimalTemperature(value) {
  return isInRange(value, 18, 28);
}

export function isOptimalHumidity(value) {
  return isInRange(value, 60, 80);
}

export function isOptimalLight(value) {
  return isInRange(value, 10000, 30000);
}

export function isOptimalCO2(value) {
  return isInRange(value, 400, 1000);
}

export function isOptimalSoilMoisture(value) {
  return isInRange(value, 50, 80);
}
