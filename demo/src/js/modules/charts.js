/**
 * EchoSmart Demo — Chart Manager
 *
 * Creates and updates Chart.js instances used across pages.
 */

import { Chart, registerables } from "chart.js";
import { getColors } from "./sensors.js";

Chart.register(...registerables);

/* ---- Shared defaults ---- */
Chart.defaults.color = "#78909C";
Chart.defaults.borderColor = "rgba(255,255,255,0.04)";
Chart.defaults.font.family =
  '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

const TOOLTIP_OPTS = {
  backgroundColor: "#111111",
  titleColor: "#E0E0E0",
  bodyColor: "#E0E0E0",
  borderColor: "rgba(255,255,255,0.1)",
  borderWidth: 1,
  cornerRadius: 8,
  padding: 10,
};

/** Generate 24-h labels ending at the current hour */
export function make24hLabels() {
  const labels = [];
  const now = new Date();
  for (let h = 23; h >= 0; h--) {
    const d = new Date(now.getTime() - h * 3600000);
    labels.push(d.getHours().toString().padStart(2, "0") + ":00");
  }
  return labels;
}

/**
 * Create a single-line area chart.
 */
export function createLineChart(canvas, label, data, color, yMin, yMax) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: make24hLabels(),
      datasets: [
        {
          label,
          data: [...data],
          borderColor: color,
          backgroundColor: color + "1A",
          fill: true,
          tension: 0.35,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { display: false },
        tooltip: TOOLTIP_OPTS,
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 8, font: { size: 11 } } },
        y: {
          min: yMin,
          max: yMax,
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { font: { size: 11 } },
        },
      },
    },
  });
}

/**
 * Create the multi-dataset "Sensor Readings" chart used in Dashboard.
 */
export function createMultiChart(canvas, sensors) {
  const COLORS = getColors();
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: make24hLabels(),
      datasets: [
        {
          label: "Temp",
          data: [...sensors.temperature.history],
          borderColor: COLORS.temperature,
          backgroundColor: COLORS.temperature + "1A",
          fill: true,
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 2,
          yAxisID: "y",
        },
        {
          label: "Humidity",
          data: [...sensors.humidity.history],
          borderColor: COLORS.humidity,
          backgroundColor: COLORS.humidity + "1A",
          fill: true,
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 2,
          yAxisID: "y1",
        },
        {
          label: "CO₂",
          data: [...sensors.co2.history],
          borderColor: COLORS.co2,
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 1.5,
          yAxisID: "y2",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 10, boxHeight: 10, borderRadius: 2, useBorderRadius: true, padding: 14, font: { size: 11 } },
        },
        tooltip: TOOLTIP_OPTS,
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 8, font: { size: 11 } } },
        y:  { type: "linear", position: "left", min: 10, max: 40, grid: { color: "rgba(255,255,255,0.04)" }, ticks: { font: { size: 11 }, callback: (v) => v + "°C" } },
        y1: { type: "linear", position: "right", min: 20, max: 100, grid: { display: false }, ticks: { font: { size: 11 }, callback: (v) => v + "%" } },
        y2: { display: false, min: 300, max: 1500 },
      },
    },
  });
}

/**
 * Create a tiny sparkline chart (no axes, no tooltips).
 */
export function createSparkline(canvas, data, color) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: data.map((_, i) => i),
      datasets: [
        {
          data: [...data],
          borderColor: color,
          backgroundColor: color + "12",
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 1.5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: { display: false },
      },
    },
  });
}

/**
 * Update chart data in-place.
 */
export function updateChartData(chart, datasetIndex, newData) {
  chart.data.datasets[datasetIndex].data = [...newData];
  chart.update("none"); // no animation for smoother live feel
}
