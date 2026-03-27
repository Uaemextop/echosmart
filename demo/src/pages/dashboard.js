/**
 * EchoSmart Demo — Dashboard Page Renderer
 */

import { formatValue, trendInfo, getColors } from "../js/modules/sensors.js";
import { createMultiChart, createSparkline, updateChartData } from "../js/modules/charts.js";
import { timeAgo } from "../js/modules/alerts.js";
import { getGateways } from "../js/modules/gateway.js";

let multiChart = null;
const sparklines = {};

/**
 * Render the dashboard page content.
 * @param {Record<string, import("../js/modules/sensors.js").SensorState>} sensors
 * @param {import("../js/modules/alerts.js").Alert[]} alerts
 */
export function renderDashboard(sensors, alerts) {
  updateSensorCards(sensors);
  updateAlertPanel(alerts);
  updateGatewayRow();

  if (!multiChart) {
    const canvas = document.getElementById("mainChart");
    if (canvas) multiChart = createMultiChart(canvas, sensors);
  }

  /* Create sparklines once */
  const COLORS = getColors();
  for (const key of Object.keys(sensors)) {
    if (!sparklines[key]) {
      const canvas = document.getElementById("spark-" + key);
      if (canvas) {
        sparklines[key] = createSparkline(canvas, sensors[key].history, COLORS[key]);
      }
    }
  }
}

/**
 * Live-update dashboard data (called every tick).
 */
export function updateDashboard(sensors, alerts) {
  updateSensorCards(sensors);
  updateAlertPanel(alerts);
  updateGatewayRow();

  if (multiChart) {
    updateChartData(multiChart, 0, sensors.temperature.history);
    updateChartData(multiChart, 1, sensors.humidity.history);
    updateChartData(multiChart, 2, sensors.co2.history);
  }

  const COLORS = getColors();
  for (const key of Object.keys(sparklines)) {
    if (sparklines[key]) {
      updateChartData(sparklines[key], 0, sensors[key].history);
    }
  }
}

function updateSensorCards(sensors) {
  const cards = [
    { key: "temperature", el: "dashTemp" },
    { key: "humidity",    el: "dashHum" },
    { key: "co2",         el: "dashCo2" },
    { key: "light",       el: "dashLight" },
    { key: "soil",        el: "dashSoil" },
  ];

  for (const c of cards) {
    const valEl = document.getElementById(c.el + "Val");
    const trendEl = document.getElementById(c.el + "Trend");
    const s = sensors[c.key];
    if (!s) continue;
    if (valEl) valEl.textContent = formatValue(c.key, s.value);
    if (trendEl) {
      const t = trendInfo(s.trend, s.spec.unit);
      trendEl.textContent = t.text;
      trendEl.className = "sensor-card__trend sensor-card__trend--" + t.dir;
    }
  }
}

function updateAlertPanel(alerts) {
  const list = document.getElementById("dashAlerts");
  if (!list) return;

  const html = alerts.slice(0, 4).map((a) => `
    <div class="alert-item alert-item--${a.severity}">
      <div class="alert-item__dot"></div>
      <div class="alert-item__content">
        <span class="alert-item__title">${a.title}</span>
        <span class="alert-item__meta">${a.zone} · ${a.sensor} · ${timeAgo(a.time)}</span>
      </div>
    </div>
  `).join("");

  list.innerHTML = html;
}

function updateGatewayRow() {
  const container = document.getElementById("gatewayRow");
  if (!container) return;

  const gws = getGateways();
  container.innerHTML = gws.map((gw) => `
    <div class="card gateway-card">
      <div class="gateway-card__header">
        <span class="status-dot status-dot--${gw.status}"></span>
        <span class="gateway-card__name">${gw.name}</span>
      </div>
      <div class="gateway-card__detail">${gw.sensors} sensores · ${gw.uptime}</div>
      <div class="gateway-card__detail text-muted">${gw.cpu}% CPU · ${gw.mem}% RAM</div>
    </div>
  `).join("");
}
