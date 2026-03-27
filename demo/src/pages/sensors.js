/**
 * EchoSmart Demo — Sensors Page Renderer
 */

import { formatValue, checkStatus, getColors, getSpecs, computeStats, generatePeriodData } from "../js/modules/sensors.js";
import { createSparkline, createLineChart, updateChartData } from "../js/modules/charts.js";
import { ICONS } from "../js/modules/icons.js";

/** Milliseconds in one hour */
const MS_PER_HOUR = 3_600_000;

const sensorMeta = [
  { key: "temperature", name: "DS18B20 #1",   type: "Temperatura",     zone: "Zona A", icon: "temperature" },
  { key: "humidity",    name: "DHT22 #1",      type: "Humedad Ambiente", zone: "Zona A", icon: "humidity" },
  { key: "co2",         name: "MH-Z19C",       type: "CO₂",             zone: "Zona A", icon: "co2" },
  { key: "light",       name: "BH1750",        type: "Luminosidad",     zone: "Zona B", icon: "light" },
  { key: "soil",        name: "Soil+ADS1115",  type: "Humedad Suelo",   zone: "Zona B", icon: "soil" },
  { key: "temperature", name: "DS18B20 #2",   type: "Temperatura",     zone: "Zona C", icon: "temperature" },
  { key: "humidity",    name: "DHT22 #2",      type: "Humedad Ambiente", zone: "Zona C", icon: "humidity" },
  { key: "co2",         name: "MH-Z19C #2",    type: "CO₂",             zone: "Zona B", icon: "co2" },
];

const sparkRefs = {};
let detailChart = null;
let selectedPeriod = "day";
let selectedSensorIdx = null;

export function renderSensors(sensors) {
  const grid = document.getElementById("sensorsGrid");
  if (!grid) return;

  const COLORS = getColors();
  const SPECS = getSpecs();

  grid.innerHTML = sensorMeta.map((m, idx) => {
    const s = sensors[m.key];
    const status = checkStatus(m.key, s.value);
    const spec = SPECS[m.key];
    const stats = computeStats(s.history);
    const statusBadge = status === "optimal"
      ? `<span class="badge badge--success">Normal</span>`
      : status === "warning"
        ? `<span class="badge badge--warning">Alerta</span>`
        : `<span class="badge badge--danger">Crítico</span>`;

    return `
      <div class="sensor-detail-card" data-idx="${idx}">
        <div class="sensor-detail-card__top">
          <div>
            <div class="sensor-detail-card__name">${m.name}</div>
            <div class="sensor-detail-card__type">${m.type} · ${m.zone}</div>
          </div>
          ${statusBadge}
        </div>
        <div class="sensor-detail-card__value" style="color: ${COLORS[m.key]}">${formatValue(m.key, s.value)}</div>
        <div class="sensor-detail-card__range">Rango óptimo: ${spec.optMin}–${spec.optMax}${spec.unit}</div>
        <div class="sensor-detail-card__stats">
          <div class="sensor-stat">
            <span class="sensor-stat__label">Mín</span>
            <span class="sensor-stat__value" data-stat="min">${formatValue(m.key, stats.min)}</span>
          </div>
          <div class="sensor-stat">
            <span class="sensor-stat__label">Máx</span>
            <span class="sensor-stat__value" data-stat="max">${formatValue(m.key, stats.max)}</span>
          </div>
          <div class="sensor-stat">
            <span class="sensor-stat__label">Prom</span>
            <span class="sensor-stat__value" data-stat="avg">${formatValue(m.key, stats.avg)}</span>
          </div>
        </div>
        <div class="sensor-detail-card__chart"><canvas id="sensorSpark${idx}"></canvas></div>
        <div class="sensor-detail-card__footer">
          <span>Última lectura: hace 3s</span>
          <span class="status-dot status-dot--online"></span>
        </div>
        <button class="sensor-detail-card__expand-btn" data-expand="${idx}">Ver detalle</button>
      </div>
    `;
  }).join("");

  /* Create sparklines */
  sensorMeta.forEach((m, idx) => {
    const canvas = document.getElementById("sensorSpark" + idx);
    if (canvas) {
      sparkRefs[idx] = createSparkline(canvas, sensors[m.key].history, COLORS[m.key]);
    }
  });

  /* Expand button listeners */
  grid.querySelectorAll(".sensor-detail-card__expand-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const idx = parseInt(btn.dataset.expand, 10);
      if (Number.isNaN(idx) || idx < 0 || idx >= sensorMeta.length) return;
      openSensorDetail(idx, sensors);
    });
  });
}

function openSensorDetail(idx, sensors) {
  selectedSensorIdx = idx;
  selectedPeriod = "day";
  const panel = document.getElementById("sensorDetailPanel");
  if (!panel) return;

  const m = sensorMeta[idx];
  const COLORS = getColors();
  const SPECS = getSpecs();
  const spec = SPECS[m.key];
  const s = sensors[m.key];
  const status = checkStatus(m.key, s.value);
  const stats = computeStats(s.history);

  const statusClass = status === "optimal" ? "success" : status === "warning" ? "warning" : "danger";

  panel.innerHTML = `
    <div class="sensor-detail-panel__header">
      <div>
        <h3 class="sensor-detail-panel__title">${m.name}</h3>
        <span class="sensor-detail-panel__subtitle">${m.type} · ${m.zone}</span>
      </div>
      <button class="btn btn--ghost sensor-detail-panel__close" id="closeDetailPanel">✕</button>
    </div>
    <div class="sensor-detail-panel__body">
      <div class="sensor-detail-panel__current">
        <span class="sensor-detail-panel__big-value" style="color: ${COLORS[m.key]}">${formatValue(m.key, s.value)}</span>
        <span class="badge badge--${statusClass}">${status === "optimal" ? "Normal" : status === "warning" ? "Alerta" : "Crítico"}</span>
      </div>
      <div class="sensor-detail-panel__info-grid">
        <div class="sensor-detail-panel__info-item">
          <span class="sensor-detail-panel__info-label">Rango óptimo</span>
          <span class="sensor-detail-panel__info-value">${spec.optMin}–${spec.optMax}${spec.unit}</span>
        </div>
        <div class="sensor-detail-panel__info-item">
          <span class="sensor-detail-panel__info-label">Rango sensor</span>
          <span class="sensor-detail-panel__info-value">${spec.min}–${spec.max}${spec.unit}</span>
        </div>
        <div class="sensor-detail-panel__info-item">
          <span class="sensor-detail-panel__info-label">Mínimo (24h)</span>
          <span class="sensor-detail-panel__info-value">${formatValue(m.key, stats.min)}</span>
        </div>
        <div class="sensor-detail-panel__info-item">
          <span class="sensor-detail-panel__info-label">Máximo (24h)</span>
          <span class="sensor-detail-panel__info-value">${formatValue(m.key, stats.max)}</span>
        </div>
        <div class="sensor-detail-panel__info-item">
          <span class="sensor-detail-panel__info-label">Promedio (24h)</span>
          <span class="sensor-detail-panel__info-value">${formatValue(m.key, stats.avg)}</span>
        </div>
        <div class="sensor-detail-panel__info-item">
          <span class="sensor-detail-panel__info-label">Estado</span>
          <span class="status-dot status-dot--online" style="display:inline-block;vertical-align:middle"></span> En línea
        </div>
      </div>
      <div class="sensor-detail-panel__period-selector">
        <button class="btn btn--period active" data-period="day">Día</button>
        <button class="btn btn--period" data-period="week">Semana</button>
        <button class="btn btn--period" data-period="month">Mes</button>
      </div>
      <div class="sensor-detail-panel__chart-wrap">
        <canvas id="detailPeriodChart"></canvas>
      </div>
      <div class="sensor-detail-panel__period-stats" id="detailPeriodStats"></div>
    </div>
  `;

  panel.classList.add("open");

  /* Close button */
  document.getElementById("closeDetailPanel")?.addEventListener("click", () => {
    panel.classList.remove("open");
    selectedSensorIdx = null;
    if (detailChart) { detailChart.destroy(); detailChart = null; }
  });

  /* Period buttons */
  panel.querySelectorAll(".btn--period").forEach((btn) => {
    btn.addEventListener("click", () => {
      panel.querySelectorAll(".btn--period").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedPeriod = btn.dataset.period;
      renderDetailChart(idx, sensors);
    });
  });

  renderDetailChart(idx, sensors);
}

function renderDetailChart(idx, sensors) {
  const m = sensorMeta[idx];
  const COLORS = getColors();
  const SPECS = getSpecs();
  const spec = SPECS[m.key];

  const canvas = document.getElementById("detailPeriodChart");
  if (!canvas) return;

  if (detailChart) { detailChart.destroy(); detailChart = null; }

  let chartData, chartLabels, stats;

  if (selectedPeriod === "day") {
    chartData = sensors[m.key].history;
    const now = new Date();
    chartLabels = chartData.map((_, i) => {
      const d = new Date(now.getTime() - (chartData.length - 1 - i) * MS_PER_HOUR);
      return d.getHours().toString().padStart(2, "0") + ":00";
    });
    stats = computeStats(chartData);
  } else {
    const period = generatePeriodData(m.key, selectedPeriod);
    chartData = period.data;
    chartLabels = period.labels;
    stats = { min: period.min, max: period.max, avg: period.avg };
  }

  detailChart = createLineChart(canvas, m.type, chartData, COLORS[m.key], spec.min, spec.max);
  detailChart.data.labels = chartLabels;
  detailChart.update();

  const periodLabel = selectedPeriod === "day" ? "24h" : selectedPeriod === "week" ? "7 días" : "30 días";
  const statsEl = document.getElementById("detailPeriodStats");
  if (statsEl) {
    statsEl.innerHTML = `
      <div class="sensor-stat sensor-stat--panel">
        <span class="sensor-stat__label">Mín (${periodLabel})</span>
        <span class="sensor-stat__value">${formatValue(m.key, stats.min)}</span>
      </div>
      <div class="sensor-stat sensor-stat--panel">
        <span class="sensor-stat__label">Máx (${periodLabel})</span>
        <span class="sensor-stat__value">${formatValue(m.key, stats.max)}</span>
      </div>
      <div class="sensor-stat sensor-stat--panel">
        <span class="sensor-stat__label">Prom (${periodLabel})</span>
        <span class="sensor-stat__value">${formatValue(m.key, stats.avg)}</span>
      </div>
    `;
  }
}

export function updateSensors(sensors) {
  const COLORS = getColors();
  sensorMeta.forEach((m, idx) => {
    const card = document.querySelector(`.sensor-detail-card[data-idx="${idx}"]`);
    if (!card) return;
    const s = sensors[m.key];
    const valEl = card.querySelector(".sensor-detail-card__value");
    if (valEl) valEl.textContent = formatValue(m.key, s.value);

    /* Update stats */
    const stats = computeStats(s.history);
    const minEl = card.querySelector('[data-stat="min"]');
    const maxEl = card.querySelector('[data-stat="max"]');
    const avgEl = card.querySelector('[data-stat="avg"]');
    if (minEl) minEl.textContent = formatValue(m.key, stats.min);
    if (maxEl) maxEl.textContent = formatValue(m.key, stats.max);
    if (avgEl) avgEl.textContent = formatValue(m.key, stats.avg);

    if (sparkRefs[idx]) {
      updateChartData(sparkRefs[idx], 0, s.history);
    }
  });

  /* Update detail panel chart if open on day view */
  if (selectedSensorIdx !== null && selectedPeriod === "day" && detailChart) {
    const m = sensorMeta[selectedSensorIdx];
    const s = sensors[m.key];
    updateChartData(detailChart, 0, s.history);
    const stats = computeStats(s.history);
    const statsEl = document.getElementById("detailPeriodStats");
    if (statsEl) {
      statsEl.innerHTML = `
        <div class="sensor-stat sensor-stat--panel">
          <span class="sensor-stat__label">Mín (24h)</span>
          <span class="sensor-stat__value">${formatValue(m.key, stats.min)}</span>
        </div>
        <div class="sensor-stat sensor-stat--panel">
          <span class="sensor-stat__label">Máx (24h)</span>
          <span class="sensor-stat__value">${formatValue(m.key, stats.max)}</span>
        </div>
        <div class="sensor-stat sensor-stat--panel">
          <span class="sensor-stat__label">Prom (24h)</span>
          <span class="sensor-stat__value">${formatValue(m.key, stats.avg)}</span>
        </div>
      `;
    }
  }
}
