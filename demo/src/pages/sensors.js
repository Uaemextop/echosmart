/**
 * EchoSmart Demo — Sensors Page Renderer
 */

import { formatValue, checkStatus, getColors, getSpecs } from "../js/modules/sensors.js";
import { createSparkline, updateChartData } from "../js/modules/charts.js";
import { ICONS } from "../js/modules/icons.js";

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

export function renderSensors(sensors) {
  const grid = document.getElementById("sensorsGrid");
  if (!grid) return;

  const COLORS = getColors();
  const SPECS = getSpecs();

  grid.innerHTML = sensorMeta.map((m, idx) => {
    const s = sensors[m.key];
    const status = checkStatus(m.key, s.value);
    const spec = SPECS[m.key];
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
        <div class="sensor-detail-card__chart"><canvas id="sensorSpark${idx}"></canvas></div>
        <div class="sensor-detail-card__footer">
          <span>Última lectura: hace 3s</span>
          <span class="status-dot status-dot--online"></span>
        </div>
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
}

export function updateSensors(sensors) {
  const COLORS = getColors();
  sensorMeta.forEach((m, idx) => {
    const card = document.querySelector(`.sensor-detail-card[data-idx="${idx}"]`);
    if (!card) return;
    const valEl = card.querySelector(".sensor-detail-card__value");
    if (valEl) valEl.textContent = formatValue(m.key, sensors[m.key].value);

    if (sparkRefs[idx]) {
      updateChartData(sparkRefs[idx], 0, sensors[m.key].history);
    }
  });
}
