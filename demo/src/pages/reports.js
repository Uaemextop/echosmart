/**
 * EchoSmart Demo — Reports Page Renderer
 *
 * Orchestrates the reports page by composing specialized modules:
 *  - gauges.js               → Semicircular gauge charts
 *  - charts.js               → Line & bar charts (Chart.js)
 *  - disease-analyzer.js     → Phytosanitary risk detection (fallback)
 *  - ai-report-renderer.js   → AI report HTML generation
 *  - pdf-export.js           → PDF export via print dialog
 *  - github-models-client.js → GitHub Models API integration (GPT-5.4)
 *
 * @module pages/reports
 */

import { Chart } from "chart.js";
import { createLineChart } from "../js/modules/charts.js";
import { getColors, getSpecs, formatValue, computeStats, checkStatus } from "../js/modules/sensors.js";
import { drawGauge } from "../js/modules/gauges.js";
import { buildReportData, buildReportDataFromAI, renderAIReportHTML } from "../js/modules/ai-report-renderer.js";
import { exportPDF } from "../js/modules/pdf-export.js";
import {
  hasToken, getStoredToken, storeToken, clearToken,
  callGitHubModels, prepareSensorData,
} from "../js/modules/github-models-client.js";

/** Track one-time Chart.js instantiation to avoid duplicates */
let chartsCreated = false;

/** Duration (ms) to display error messages before auto-removal */
const ERROR_DISPLAY_MS = 8000;

/** Sensor metadata used across summary cards and gauges */
const SENSOR_META = [
  { key: "temperature", label: "Temperatura", icon: "🌡️", unit: "°C" },
  { key: "humidity",    label: "Humedad",     icon: "💧", unit: "%" },
  { key: "co2",         label: "CO₂",         icon: "☁️", unit: "ppm" },
  { key: "light",       label: "Luminosidad", icon: "☀️", unit: "lux" },
  { key: "soil",        label: "Suelo",       icon: "🌱", unit: "%" },
];

/** Line chart configurations */
const LINE_CHART_CONFIGS = [
  { id: "reportTempChart",  label: "Temperatura (°C)", key: "temperature", yMin: 10,  yMax: 40 },
  { id: "reportHumChart",   label: "Humedad (%)",      key: "humidity",    yMin: 20,  yMax: 100 },
  { id: "reportCo2Chart",   label: "CO₂ (ppm)",        key: "co2",         yMin: 300, yMax: 1500 },
  { id: "reportLightChart", label: "Luminosidad (lux)", key: "light",       yMin: 0,   yMax: 50000 },
];

/** Gauge chart configurations (subset of sensors with gauges) */
const GAUGE_CONFIGS = [
  { id: "gaugeTemp", key: "temperature", unit: "°C" },
  { id: "gaugeHum",  key: "humidity",    unit: "%" },
  { id: "gaugeCo2",  key: "co2",         unit: "ppm" },
  { id: "gaugeSoil", key: "soil",        unit: "%" },
];

/**
 * Render / update the Reports page.
 * @param {Record<string, import("../js/modules/sensors.js").SensorState>} sensors
 */
export function renderReports(sensors) {
  const COLORS = getColors();
  const SPECS = getSpecs();

  _renderSummaryCards(sensors, COLORS);
  _renderGauges(sensors, SPECS, COLORS);
  _renderCharts(sensors, COLORS);
  _renderAIReport(sensors);
  _bindExportButton();
}

/* ===== Private section renderers ===== */

/**
 * Populate the statistics summary cards row.
 */
function _renderSummaryCards(sensors, COLORS) {
  const container = document.getElementById("reportsSummary");
  if (!container) return;

  container.innerHTML = SENSOR_META.map(meta => {
    const stats = computeStats(sensors[meta.key].history);
    const status = checkStatus(meta.key, sensors[meta.key].value);
    const badgeClass = status === "optimal" ? "success" : status === "warning" ? "warning" : "danger";
    const badgeLabel = status === "optimal" ? "Normal" : status === "warning" ? "Alerta" : "Crítico";

    return `
      <div class="report-summary-card">
        <div class="report-summary-card__header">
          <span class="report-summary-card__icon">${meta.icon}</span>
          <span class="report-summary-card__label">${meta.label}</span>
          <span class="badge badge--${badgeClass}">${badgeLabel}</span>
        </div>
        <div class="report-summary-card__value" style="color:${COLORS[meta.key]}">${formatValue(meta.key, sensors[meta.key].value)}</div>
        <div class="report-summary-card__stats">
          <span>Mín: ${formatValue(meta.key, stats.min)}</span>
          <span>Máx: ${formatValue(meta.key, stats.max)}</span>
          <span>Prom: ${formatValue(meta.key, stats.avg)}</span>
        </div>
      </div>
    `;
  }).join("");
}

/**
 * Draw gauge charts for key sensors.
 */
function _renderGauges(sensors, SPECS, COLORS) {
  GAUGE_CONFIGS.forEach(cfg => {
    const spec = SPECS[cfg.key];
    drawGauge(cfg.id, sensors[cfg.key].value, spec.min, spec.max, spec.optMin, spec.optMax, COLORS[cfg.key], cfg.unit);
  });
}

/**
 * Create line charts and bar chart (once only).
 */
function _renderCharts(sensors, COLORS) {
  if (chartsCreated) return;
  chartsCreated = true;

  LINE_CHART_CONFIGS.forEach(cfg => {
    const canvas = document.getElementById(cfg.id);
    if (canvas && sensors[cfg.key]) {
      createLineChart(canvas, cfg.label, sensors[cfg.key].history, COLORS[cfg.key], cfg.yMin, cfg.yMax);
    }
  });

  _createBarChart("reportBarChart", sensors, COLORS);
}

/** Reference to current sensors for AI regeneration */
let _currentSensors = null;

/**
 * Generate and insert the AI analysis report (fallback mode initially).
 */
function _renderAIReport(sensors) {
  _currentSensors = sensors;
  const container = document.getElementById("aiReportContent");
  if (!container) return;

  const reportData = buildReportData(sensors);
  container.innerHTML = renderAIReportHTML(sensors, reportData);

  _renderTokenUI();
}

/**
 * Render the token input and "Generate with AI" button UI.
 */
function _renderTokenUI() {
  const tokenArea = document.getElementById("aiTokenArea");
  if (!tokenArea) return;

  const connected = hasToken();
  tokenArea.innerHTML = connected
    ? `
      <div class="ai-token-status ai-token-status--connected">
        <span class="ai-token-status__dot"></span>
        <span>Token configurado</span>
        <button class="btn btn--ghost btn--sm" id="aiGenerateBtn">🤖 Generar análisis con IA</button>
        <button class="btn btn--ghost btn--sm btn--danger" id="aiDisconnectBtn">Desconectar</button>
      </div>
    `
    : `
      <div class="ai-token-form">
        <label class="ai-token-form__label">
          🔑 Ingresa tu token de GitHub Models para análisis con IA en vivo:
        </label>
        <div class="ai-token-form__row">
          <input type="password" class="ai-token-form__input" id="aiTokenInput"
                 placeholder="github_pat_..." autocomplete="off" />
          <button class="btn btn--primary btn--sm" id="aiConnectBtn">Conectar</button>
        </div>
        <p class="ai-token-form__hint">
          El token se almacena solo en tu sesión del navegador (sessionStorage) y nunca se guarda en el código fuente.
          Obtén un token en <a href="https://github.com/settings/tokens" target="_blank" rel="noopener">GitHub Settings → Tokens</a>.
        </p>
      </div>
    `;

  /* Bind connect button */
  const connectBtn = document.getElementById("aiConnectBtn");
  if (connectBtn) {
    connectBtn.addEventListener("click", () => {
      const input = document.getElementById("aiTokenInput");
      const token = input?.value?.trim();
      if (!token) return;
      storeToken(token);
      _renderTokenUI();
    });
  }

  /* Bind disconnect button */
  const disconnectBtn = document.getElementById("aiDisconnectBtn");
  if (disconnectBtn) {
    disconnectBtn.addEventListener("click", () => {
      clearToken();
      _renderTokenUI();
      /* Re-render with fallback */
      if (_currentSensors) {
        const container = document.getElementById("aiReportContent");
        if (container) {
          const reportData = buildReportData(_currentSensors);
          container.innerHTML = renderAIReportHTML(_currentSensors, reportData);
          _renderTokenUI();
        }
      }
    });
  }

  /* Bind generate button */
  const generateBtn = document.getElementById("aiGenerateBtn");
  if (generateBtn) {
    generateBtn.addEventListener("click", () => _generateWithAI());
  }
}

/**
 * Call GitHub Models API and re-render the AI report with real AI content.
 */
async function _generateWithAI() {
  const sensors = _currentSensors;
  if (!sensors) return;

  const token = getStoredToken();
  if (!token) return;

  const container = document.getElementById("aiReportContent");
  const generateBtn = document.getElementById("aiGenerateBtn");
  if (!container) return;

  /* Show loading state */
  if (generateBtn) {
    generateBtn.disabled = true;
    generateBtn.textContent = "⏳ Generando análisis…";
  }

  try {
    const stats = {
      temp:  computeStats(sensors.temperature.history),
      hum:   computeStats(sensors.humidity.history),
      co2:   computeStats(sensors.co2.history),
      light: computeStats(sensors.light.history),
      soil:  computeStats(sensors.soil.history),
    };

    const sensorData = prepareSensorData(sensors, stats);
    const aiResponse = await callGitHubModels(token, sensorData);
    const reportData = buildReportDataFromAI(sensors, aiResponse);
    container.innerHTML = renderAIReportHTML(sensors, reportData);
    _renderTokenUI();
  } catch (err) {
    /* Show error and restore button */
    if (generateBtn) {
      generateBtn.disabled = false;
      generateBtn.textContent = "🤖 Generar análisis con IA";
    }
    const errorEl = document.createElement("div");
    errorEl.className = "ai-report__error";
    errorEl.textContent = `Error: ${err.message}`;
    container.prepend(errorEl);
    setTimeout(() => errorEl.remove(), ERROR_DISPLAY_MS);
  }
}

/**
 * Bind the PDF export button (once only).
 */
function _bindExportButton() {
  const btn = document.getElementById("exportPdfBtn");
  if (!btn || btn.dataset.bound) return;

  btn.dataset.bound = "true";
  btn.addEventListener("click", exportPDF);
}

/**
 * Create a bar chart comparing all sensors as percentage of their range.
 */
function _createBarChart(canvasId, sensors, COLORS) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const SPECS = getSpecs();
  const keys = SENSOR_META.map(m => m.key);
  const labels = SENSOR_META.map(m => m.label.substring(0, 7));

  const normalizedValues = keys.map(k => {
    const spec = SPECS[k];
    return ((sensors[k].value - spec.min) / (spec.max - spec.min)) * 100;
  });

  return new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Nivel actual (%)",
        data: normalizedValues,
        backgroundColor: keys.map(k => COLORS[k] + "40"),
        borderColor: keys.map(k => COLORS[k]),
        borderWidth: 1.5,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111111",
          titleColor: "#E0E0E0",
          bodyColor: "#E0E0E0",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          cornerRadius: 8,
          callbacks: {
            label: (ctx) => `${ctx.parsed.y.toFixed(1)}% del rango`,
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: {
          min: 0, max: 100,
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { font: { size: 11 }, callback: (v) => v + "%" },
        },
      },
    },
  });
}
