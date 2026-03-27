/**
 * EchoSmart Demo — Disease Risk Analyzer
 *
 * Analyzes greenhouse environmental conditions to detect
 * phytosanitary risks and generate actionable alerts.
 *
 * Simulates the analysis that would be performed by GitHub Models (GPT-5.4)
 * in a production environment with real API integration.
 *
 * @module disease-analyzer
 */

/** @typedef {{ name: string, risk: "ALTO"|"MEDIO"|"BAJO", color: string, reason: string, action: string }} DiseaseAlert */

/** Alert severity colors */
const RISK_COLORS = {
  ALTO:  "#FF1744",
  MEDIO: "#FF9100",
  BAJO:  "#00E676",
};

/** Environmental thresholds for disease detection */
const THRESHOLDS = {
  botrytis: { humHigh: 85, humMed: 75, tempHigh: 25 },
  thermalStress: { tempCritical: 30, tempWarning: 28 },
  coldDamage: { tempCritical: 15 },
  mildew: { humHigh: 80, tempLow: 20, tempHigh: 28 },
  co2Toxicity: { co2High: 1000 },
  soilDrought: { soilCritical: 40, soilWarning: 50 },
  lightDeficiency: { lightLow: 5000 },
};

/**
 * Analyze sensor data and return a list of disease/risk alerts.
 * @param {Record<string, { value: number }>} sensors
 * @returns {DiseaseAlert[]}
 */
export function analyzeDiseases(sensors) {
  const alerts = [];

  _checkBotrytis(sensors, alerts);
  _checkThermalStress(sensors, alerts);
  _checkColdDamage(sensors, alerts);
  _checkMildew(sensors, alerts);
  _checkCo2Toxicity(sensors, alerts);
  _checkSoilDrought(sensors, alerts);
  _checkLightDeficiency(sensors, alerts);

  if (alerts.length === 0) {
    alerts.push({
      name: "Sin riesgos detectados",
      risk: "BAJO",
      color: RISK_COLORS.BAJO,
      reason: "Todas las condiciones ambientales están dentro de los rangos óptimos para el cultivo en invernadero.",
      action: "Continuar con el monitoreo regular. Mantener las prácticas actuales de manejo ambiental.",
    });
  }

  return alerts;
}

/* ---- Individual disease checkers (Single Responsibility) ---- */

function _checkBotrytis(sensors, alerts) {
  const { humHigh, humMed, tempHigh } = THRESHOLDS.botrytis;
  const hum = sensors.humidity.value;
  const temp = sensors.temperature.value;

  if (hum > humHigh && temp > tempHigh) {
    alerts.push({
      name: "Botrytis cinerea (Moho gris)",
      risk: "ALTO",
      color: RISK_COLORS.ALTO,
      reason: `Humedad ${hum.toFixed(0)}% > ${humHigh}% combinada con temperatura ${temp.toFixed(1)}°C > ${tempHigh}°C crea condiciones ideales para proliferación de esporas.`,
      action: "Reducir humedad inmediatamente. Aumentar ventilación. Aplicar fungicida preventivo a base de iprodiona.",
    });
  } else if (hum > humMed) {
    alerts.push({
      name: "Botrytis cinerea (Moho gris)",
      risk: "MEDIO",
      color: RISK_COLORS.MEDIO,
      reason: `Humedad ${hum.toFixed(0)}% cercana al umbral crítico de ${humHigh}%. La combinación con temperatura actual de ${temp.toFixed(1)}°C puede favorecer condiciones de propagación.`,
      action: "Monitorear continuamente. Mejorar la circulación de aire entre plantas. Considerar deshumidificación preventiva.",
    });
  }
}

function _checkThermalStress(sensors, alerts) {
  const { tempCritical, tempWarning } = THRESHOLDS.thermalStress;
  const temp = sensors.temperature.value;

  if (temp > tempCritical) {
    alerts.push({
      name: "Estrés térmico / Marchitamiento",
      risk: "ALTO",
      color: RISK_COLORS.ALTO,
      reason: `Temperatura ${temp.toFixed(1)}°C excede significativamente el rango óptimo de 18–28°C. Las plantas sufren daño celular y reducción en la fotosíntesis.`,
      action: "Activar sistema de enfriamiento. Aumentar riego por aspersión. Usar mallas de sombreo al 50%.",
    });
  } else if (temp > tempWarning) {
    alerts.push({
      name: "Estrés térmico leve",
      risk: "MEDIO",
      color: RISK_COLORS.MEDIO,
      reason: `Temperatura ${temp.toFixed(1)}°C en el límite superior del rango óptimo. Prolongar esta condición puede reducir el rendimiento de los cultivos.`,
      action: "Verificar sistema de ventilación. Preparar enfriamiento adicional si la tendencia continúa.",
    });
  }
}

function _checkColdDamage(sensors, alerts) {
  const temp = sensors.temperature.value;

  if (temp < THRESHOLDS.coldDamage.tempCritical) {
    alerts.push({
      name: "Daño por frío / Helada",
      risk: "ALTO",
      color: RISK_COLORS.ALTO,
      reason: `Temperatura ${temp.toFixed(1)}°C muy por debajo del rango óptimo. Riesgo de daño celular por cristalización del agua intracelular.`,
      action: "Activar calefacción de emergencia. Cerrar ventilaciones. Cubrir cultivos sensibles con manta térmica.",
    });
  }
}

function _checkMildew(sensors, alerts) {
  const { humHigh, tempLow, tempHigh } = THRESHOLDS.mildew;
  const hum = sensors.humidity.value;
  const temp = sensors.temperature.value;

  if (hum > humHigh && temp > tempLow && temp < tempHigh) {
    alerts.push({
      name: "Mildiu (Peronospora spp.)",
      risk: "MEDIO",
      color: RISK_COLORS.MEDIO,
      reason: `Humedad relativa ${hum.toFixed(0)}% > ${humHigh}% con temperatura entre ${tempLow}–${tempHigh}°C (actual: ${temp.toFixed(1)}°C). Estas condiciones permiten la germinación de esporas de mildiu.`,
      action: "Aplicar fungicida preventivo a base de metalaxil. Reducir densidad de follaje. Mejorar drenaje.",
    });
  }
}

function _checkCo2Toxicity(sensors, alerts) {
  const co2 = sensors.co2.value;

  if (co2 > THRESHOLDS.co2Toxicity.co2High) {
    alerts.push({
      name: "Exceso de CO₂ — Toxicidad",
      risk: "MEDIO",
      color: RISK_COLORS.MEDIO,
      reason: `Nivel de CO₂ ${co2.toFixed(0)} ppm supera el umbral de ${THRESHOLDS.co2Toxicity.co2High} ppm. Concentraciones elevadas pueden causar cierre estomático y reducción en la transpiración.`,
      action: "Incrementar ventilación natural o forzada. Verificar fuentes de combustión. Revisar generadores de CO₂.",
    });
  }
}

function _checkSoilDrought(sensors, alerts) {
  const { soilCritical, soilWarning } = THRESHOLDS.soilDrought;
  const soil = sensors.soil.value;

  if (soil < soilCritical) {
    alerts.push({
      name: "Déficit hídrico / Estrés por sequía",
      risk: "ALTO",
      color: RISK_COLORS.ALTO,
      reason: `Humedad del suelo ${soil.toFixed(0)}% por debajo del mínimo óptimo de ${soilWarning}%. Las raíces no pueden absorber nutrientes adecuadamente.`,
      action: "Activar riego de emergencia. Verificar sistema de irrigación por goteo. Aplicar mulch para retención de humedad.",
    });
  } else if (soil < soilWarning) {
    alerts.push({
      name: "Humedad de suelo baja",
      risk: "MEDIO",
      color: RISK_COLORS.MEDIO,
      reason: `Humedad del suelo ${soil.toFixed(0)}% se acerca al límite inferior óptimo de ${soilWarning}%. Las plantas pueden mostrar signos de estrés hídrico leve.`,
      action: "Programar riego adicional. Monitorear curva de evapotranspiración.",
    });
  }
}

function _checkLightDeficiency(sensors, alerts) {
  const light = sensors.light.value;

  if (light < THRESHOLDS.lightDeficiency.lightLow) {
    alerts.push({
      name: "Deficiencia lumínica",
      risk: "MEDIO",
      color: RISK_COLORS.MEDIO,
      reason: `Luminosidad ${light.toFixed(0)} lux por debajo del mínimo óptimo de 10,000 lux. Insuficiente para fotosíntesis eficiente en la mayoría de cultivos de invernadero.`,
      action: "Activar iluminación suplementaria LED. Limpiar cubiertas de invernadero. Verificar horario de luz.",
    });
  }
}
