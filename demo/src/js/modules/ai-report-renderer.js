/**
 * EchoSmart Demo — AI Report HTML Renderer
 *
 * Generates the branded HTML for the AI analysis report,
 * including executive summary, disease alerts, environmental
 * diagram, optimal ranges schema, and engineering recommendations.
 *
 * Supports two modes:
 *  1. Real AI — Uses GitHub Models (GPT-5.4) API response
 *  2. Fallback — Uses local disease-analyzer when API unavailable
 *
 * @module ai-report-renderer
 */

import { getColors, getSpecs, formatValue, computeStats, checkStatus } from "./sensors.js";
import { analyzeDiseases } from "./disease-analyzer.js";

/** Alert severity colors */
const RISK_COLORS = { ALTO: "#FF1744", MEDIO: "#FF9100", BAJO: "#00E676" };

/** Zone C temperature offset relative to Zone A */
const ZONE_C_TEMP_OFFSET = -1.2;

/**
 * Build the full AI report data object from current sensor state.
 * @param {Record<string, { value: number, history: number[] }>} sensors
 * @returns {object} Report data with stats, diseases, and formatted dates
 */
export function buildReportData(sensors) {
  const now = new Date();

  return {
    dateStr: now.toLocaleDateString("es-MX", { year: "numeric", month: "long", day: "numeric" }),
    timeStr: now.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" }),
    tempStats:  computeStats(sensors.temperature.history),
    humStats:   computeStats(sensors.humidity.history),
    co2Stats:   computeStats(sensors.co2.history),
    lightStats: computeStats(sensors.light.history),
    soilStats:  computeStats(sensors.soil.history),
    diseases:   analyzeDiseases(sensors),
  };
}

/**
 * Build report data using real AI response from GitHub Models.
 * Falls back to local analysis for fields not provided by the AI.
 * @param {Record<string, { value: number, history: number[] }>} sensors
 * @param {object} aiResponse — Parsed JSON from GitHub Models API
 * @returns {object} Report data compatible with renderAIReportHTML
 */
export function buildReportDataFromAI(sensors, aiResponse) {
  const now = new Date();

  const diseases = (aiResponse.enfermedades || []).map(d => ({
    name: d.nombre,
    risk: d.riesgo,
    color: RISK_COLORS[d.riesgo] || RISK_COLORS.BAJO,
    reason: d.analisis,
    action: d.accion,
  }));

  if (diseases.length === 0) {
    diseases.push({
      name: "Sin riesgos detectados",
      risk: "BAJO",
      color: RISK_COLORS.BAJO,
      reason: aiResponse.resumen || "Todas las condiciones ambientales están dentro de los rangos óptimos.",
      action: "Continuar con el monitoreo regular.",
    });
  }

  return {
    dateStr: now.toLocaleDateString("es-MX", { year: "numeric", month: "long", day: "numeric" }),
    timeStr: now.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" }),
    tempStats:  computeStats(sensors.temperature.history),
    humStats:   computeStats(sensors.humidity.history),
    co2Stats:   computeStats(sensors.co2.history),
    lightStats: computeStats(sensors.light.history),
    soilStats:  computeStats(sensors.soil.history),
    diseases,
    aiSummary: aiResponse.resumen || null,
    aiRecommendations: aiResponse.recomendaciones || null,
    isAIGenerated: true,
  };
}

/**
 * Render the complete AI report HTML.
 * @param {Record<string, { value: number, history: number[] }>} sensors
 * @param {object} report — Output from buildReportData() or buildReportDataFromAI()
 * @returns {string} HTML string
 */
export function renderAIReportHTML(sensors, report) {
  const COLORS = getColors();
  const isAI = report.isAIGenerated === true;

  return `
    <div class="ai-report" id="aiReportPrintable">
      ${_renderBrandHeader(report)}
      ${_renderModelInfo(isAI)}
      ${report.aiSummary ? `<div class="ai-report__section"><h3 class="ai-report__section-title">📝 Análisis General (IA)</h3><p class="ai-report__ai-summary">${report.aiSummary}</p></div>` : ""}
      ${_renderExecutiveSummary(sensors, report, COLORS)}
      ${_renderDiseaseAlerts(report)}
      ${_renderEnvironmentDiagram(sensors, COLORS)}
      ${_renderOptimalRangesTable(sensors, COLORS)}
      ${_renderEngineeringRecommendations(report)}
      ${_renderFooter(report)}
    </div>
  `;
}

/* ===== Section Renderers (each with a single responsibility) ===== */

function _renderBrandHeader(report) {
  return `
    <div class="ai-report__brand-header">
      <div class="ai-report__brand-logo">
        <svg viewBox="0 0 120 120" fill="none" width="40" height="40">
          <defs>
            <linearGradient id="rlg" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#00E676"/><stop offset="100%" stop-color="#2E7D32"/>
            </linearGradient>
            <linearGradient id="rsg" x1="0%" y1="50%" x2="100%" y2="50%">
              <stop offset="0%" stop-color="#00BCD4"/><stop offset="100%" stop-color="#00838F"/>
            </linearGradient>
          </defs>
          <path d="M30 95Q18 55 45 28Q58 15 78 15Q88 15 95 20Q95 35 88 52Q72 85 35 95Q32 95 30 95z" fill="url(#rlg)" opacity="0.9"/>
          <path d="M72 28a20 20 0 0 1 14 14" stroke="url(#rsg)" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.9"/>
          <path d="M78 18a30 30 0 0 1 22 22" stroke="url(#rsg)" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.6"/>
        </svg>
        <div>
          <div class="ai-report__brand-name">EchoSmart</div>
          <div class="ai-report__brand-subtitle">Invernadero Inteligente — Reporte de Análisis IA</div>
        </div>
      </div>
      <div class="ai-report__brand-date">
        <div>${report.dateStr}</div>
        <div class="text-muted">${report.timeStr} hrs</div>
      </div>
    </div>
  `;
}

function _renderModelInfo(isAI) {
  const badge = isAI
    ? "🤖 GitHub Models · GPT-5.4 · Respuesta en vivo"
    : "🤖 GitHub Models · GPT-5.4 · Demo";
  const text = isAI
    ? "Análisis generado en tiempo real por inteligencia artificial usando GitHub Models API (openai/gpt-5.4)"
    : "Análisis generado localmente. Configura tu token de GitHub Models para obtener análisis con IA en vivo usando GPT-5.4.";

  return `
    <div class="ai-report__model-info">
      <span class="ai-report__model-badge">${badge}</span>
      <span class="ai-report__model-text">${text}</span>
    </div>
  `;
}

function _renderExecutiveSummary(sensors, report, COLORS) {
  const summaryItems = [
    { label: "Temperatura", value: `${sensors.temperature.value.toFixed(1)}°C`, range: `${report.tempStats.min}–${report.tempStats.max}°C`, color: COLORS.temperature },
    { label: "Humedad", value: `${sensors.humidity.value.toFixed(0)}%`, range: `${report.humStats.min}–${report.humStats.max}%`, color: COLORS.humidity },
    { label: "CO₂", value: `${sensors.co2.value.toFixed(0)} ppm`, range: `${report.co2Stats.min}–${report.co2Stats.max} ppm`, color: COLORS.co2 },
    { label: "Luminosidad", value: `${sensors.light.value.toFixed(0)} lux`, range: `${report.lightStats.min}–${report.lightStats.max} lux`, color: COLORS.light },
    { label: "Suelo", value: `${sensors.soil.value.toFixed(0)}%`, range: `${report.soilStats.min}–${report.soilStats.max}%`, color: COLORS.soil },
  ];

  return `
    <div class="ai-report__section">
      <h3 class="ai-report__section-title">📊 Resumen Ejecutivo</h3>
      <div class="ai-report__summary-grid">
        ${summaryItems.map(item => `
          <div class="ai-report__summary-item">
            <span class="ai-report__summary-label">${item.label}</span>
            <span class="ai-report__summary-value" style="color:${item.color}">${item.value}</span>
            <span class="ai-report__summary-range">Rango 24h: ${item.range}</span>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function _renderDiseaseAlerts(report) {
  return `
    <div class="ai-report__section">
      <h3 class="ai-report__section-title">⚠️ Alertas de Enfermedades y Riesgos</h3>
      <p class="ai-report__instruction-note">
        <strong>Instrucciones al modelo IA:</strong> Analizar condiciones ambientales del invernadero.
        Identificar riesgos fitosanitarios basados en combinaciones de temperatura, humedad relativa,
        CO₂, luminosidad y humedad del suelo. Correlacionar con patógenos comunes en cultivos de invernadero.
        Priorizar alertas por nivel de riesgo y proporcionar acciones correctivas específicas.
      </p>
      ${report.diseases.map(d => `
        <div class="ai-report__alert-card" style="border-left: 3px solid ${d.color}">
          <div class="ai-report__alert-header">
            <span class="ai-report__alert-name">${d.name}</span>
            <span class="ai-report__alert-risk" style="background: ${d.color}20; color: ${d.color}">${d.risk}</span>
          </div>
          <div class="ai-report__alert-reason">
            <strong>Análisis:</strong> ${d.reason}
          </div>
          <div class="ai-report__alert-action">
            <strong>Acción recomendada:</strong> ${d.action}
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function _renderEnvironmentDiagram(sensors, COLORS) {
  const temp = sensors.temperature.value;
  const hum = sensors.humidity.value;
  const co2 = sensors.co2.value;
  const light = sensors.light.value;
  const soil = sensors.soil.value;
  const tempC = (temp + ZONE_C_TEMP_OFFSET).toFixed(1);

  return `
    <div class="ai-report__section">
      <h3 class="ai-report__section-title">🏗️ Diagrama de Condiciones Ambientales</h3>
      <div class="ai-report__diagram">
        <svg viewBox="0 0 600 280" class="ai-report__diagram-svg">
          <path d="M50 220 L50 100 L300 30 L550 100 L550 220 Z" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2"/>
          <path d="M50 100 L300 30 L550 100" fill="rgba(0,230,118,0.05)" stroke="rgba(0,230,118,0.3)" stroke-width="1.5"/>
          <line x1="50" y1="220" x2="550" y2="220" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>

          <rect x="70" y="110" width="150" height="100" rx="4" fill="${COLORS.temperature}15" stroke="${COLORS.temperature}40" stroke-width="1"/>
          <text x="145" y="135" text-anchor="middle" fill="${COLORS.temperature}" font-size="12" font-weight="600">Zona A</text>
          <text x="145" y="155" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="700">${temp.toFixed(1)}°C</text>
          <text x="145" y="175" text-anchor="middle" fill="${COLORS.humidity}" font-size="11">${hum.toFixed(0)}% HR</text>
          <text x="145" y="195" text-anchor="middle" fill="${COLORS.co2}" font-size="10">${co2.toFixed(0)} ppm CO₂</text>

          <rect x="230" y="110" width="140" height="100" rx="4" fill="${COLORS.light}15" stroke="${COLORS.light}40" stroke-width="1"/>
          <text x="300" y="135" text-anchor="middle" fill="${COLORS.light}" font-size="12" font-weight="600">Zona B</text>
          <text x="300" y="155" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="700">${light.toFixed(0)} lux</text>
          <text x="300" y="175" text-anchor="middle" fill="${COLORS.soil}" font-size="11">${soil.toFixed(0)}% Suelo</text>
          <text x="300" y="195" text-anchor="middle" fill="${COLORS.co2}" font-size="10">${co2.toFixed(0)} ppm CO₂</text>

          <rect x="380" y="110" width="150" height="100" rx="4" fill="${COLORS.humidity}15" stroke="${COLORS.humidity}40" stroke-width="1"/>
          <text x="455" y="135" text-anchor="middle" fill="${COLORS.humidity}" font-size="12" font-weight="600">Zona C</text>
          <text x="455" y="155" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="700">${tempC}°C</text>
          <text x="455" y="175" text-anchor="middle" fill="${COLORS.humidity}" font-size="11">${hum.toFixed(0)}% HR</text>

          <circle cx="110" cy="150" r="5" fill="${COLORS.temperature}"/>
          <circle cx="180" cy="170" r="5" fill="${COLORS.humidity}"/>
          <circle cx="280" cy="160" r="5" fill="${COLORS.light}"/>
          <circle cx="320" cy="180" r="5" fill="${COLORS.soil}"/>
          <circle cx="430" cy="150" r="5" fill="${COLORS.temperature}"/>
          <circle cx="480" cy="170" r="5" fill="${COLORS.humidity}"/>

          <text x="300" y="260" text-anchor="middle" fill="#546e7a" font-size="11">Distribución de sensores — Invernadero Principal</text>
        </svg>
      </div>
    </div>
  `;
}

function _renderOptimalRangesTable(sensors, COLORS) {
  const SPECS = getSpecs();
  const sensorMeta = [
    { key: "temperature", label: "Temperatura", icon: "🌡️" },
    { key: "humidity",    label: "Humedad",     icon: "💧" },
    { key: "co2",         label: "CO₂",         icon: "☁️" },
    { key: "light",       label: "Luminosidad", icon: "☀️" },
    { key: "soil",        label: "Suelo",       icon: "🌱" },
  ];

  const rows = sensorMeta.map(s => {
    const spec = SPECS[s.key];
    const val = sensors[s.key].value;
    const status = checkStatus(s.key, val);
    const statusLabel = status === "optimal" ? "✅ Normal" : status === "warning" ? "⚠️ Alerta" : "🔴 Crítico";
    const pct = ((val - spec.min) / (spec.max - spec.min)) * 100;
    const optStartPct = ((spec.optMin - spec.min) / (spec.max - spec.min)) * 100;
    const optEndPct = ((spec.optMax - spec.min) / (spec.max - spec.min)) * 100;

    return `
      <tr>
        <td>${s.icon} ${s.label}</td>
        <td style="color:${COLORS[s.key]};font-weight:600">${formatValue(s.key, val)}</td>
        <td>${spec.optMin}–${spec.optMax}${spec.unit}</td>
        <td>${spec.min}–${spec.max}${spec.unit}</td>
        <td>${statusLabel}</td>
        <td>
          <div class="ai-report__scale-bar">
            <div class="ai-report__scale-optimal" style="left:${optStartPct}%;width:${optEndPct - optStartPct}%"></div>
            <div class="ai-report__scale-marker" style="left:${Math.min(100, Math.max(0, pct))}%;background:${COLORS[s.key]}"></div>
          </div>
        </td>
      </tr>
    `;
  }).join("");

  return `
    <div class="ai-report__section">
      <h3 class="ai-report__section-title">📐 Esquema de Rangos Óptimos</h3>
      <div class="ai-report__ranges-table">
        <table class="ai-report__table">
          <thead>
            <tr>
              <th>Parámetro</th>
              <th>Valor Actual</th>
              <th>Rango Óptimo</th>
              <th>Rango Sensor</th>
              <th>Estado</th>
              <th>Escala Visual</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>
  `;
}

function _renderEngineeringRecommendations(report) {
  const defaultRecs = [
    {
      title: "Calibración de Sensores",
      text: "Verificar calibración del sensor DS18B20 cada 30 días. Desviación máxima aceptable: ±0.5°C. Comparar con termómetro de referencia certificado.",
    },
    {
      title: "Mantenimiento de Ventilación",
      text: "Inspeccionar motores de ventilación y filtros. Limpiar filtros cada 15 días. Verificar apertura/cierre automatizado de ventanas cenitales y laterales.",
    },
    {
      title: "Sistema de Riego",
      text: "Revisar goteros y electroválvulas. Verificar presión del sistema (1.5–2.5 bar). Monitorear uniformidad de distribución con coeficiente de Christiansen > 85%.",
    },
    {
      title: "Monitoreo de CO₂",
      text: "Calibrar sensor MH-Z19C con gas de referencia (400 ppm). Verificar sellado del invernadero para eficiencia de inyección de CO₂. Evaluar costo-beneficio de enriquecimiento carbónico.",
    },
  ];

  /* Use AI recommendations if available, otherwise use defaults */
  const recommendations = (report.aiRecommendations && report.aiRecommendations.length > 0)
    ? report.aiRecommendations.map(r => ({ title: r.titulo, text: r.descripcion }))
    : defaultRecs;

  return `
    <div class="ai-report__section">
      <h3 class="ai-report__section-title">🔧 Recomendaciones para el Ingeniero</h3>
      <div class="ai-report__recommendations">
        ${recommendations.map((rec, i) => `
          <div class="ai-report__rec-item">
            <div class="ai-report__rec-number">${i + 1}</div>
            <div>
              <div class="ai-report__rec-title">${rec.title}</div>
              <div class="ai-report__rec-text">${rec.text}</div>
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function _renderFooter(report) {
  return `
    <div class="ai-report__footer">
      <div class="ai-report__footer-brand">
        <svg viewBox="0 0 120 120" fill="none" width="20" height="20">
          <path d="M30 95Q18 55 45 28Q58 15 78 15Q88 15 95 20Q95 35 88 52Q72 85 35 95Q32 95 30 95z" fill="#00E676" opacity="0.9"/>
        </svg>
        <span>EchoSmart · Invernadero Inteligente</span>
      </div>
      <div class="ai-report__footer-meta">
        Reporte generado el ${report.dateStr} a las ${report.timeStr} · Análisis por GitHub Models (GPT-5.4) · v1.0.0
      </div>
      <div class="ai-report__footer-disclaimer">
        Este reporte es generado por inteligencia artificial con fines informativos. Las recomendaciones deben ser evaluadas por un ingeniero agrónomo antes de su implementación.
      </div>
    </div>
  `;
}
