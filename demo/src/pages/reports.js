/**
 * EchoSmart Demo — Reports Page Renderer
 */

import { createLineChart } from "../js/modules/charts.js";
import { getColors } from "../js/modules/sensors.js";

let chartsCreated = false;

export function renderReports(sensors) {
  if (chartsCreated) return;
  chartsCreated = true;

  const COLORS = getColors();

  const configs = [
    { id: "reportTempChart",  label: "Temperatura (°C)", key: "temperature", yMin: 10, yMax: 40 },
    { id: "reportHumChart",   label: "Humedad (%)",       key: "humidity",    yMin: 20, yMax: 100 },
    { id: "reportCo2Chart",   label: "CO₂ (ppm)",         key: "co2",         yMin: 300, yMax: 1500 },
    { id: "reportLightChart", label: "Luminosidad (lux)", key: "light",       yMin: 0, yMax: 50000 },
  ];

  for (const cfg of configs) {
    const canvas = document.getElementById(cfg.id);
    if (canvas && sensors[cfg.key]) {
      createLineChart(canvas, cfg.label, sensors[cfg.key].history, COLORS[cfg.key], cfg.yMin, cfg.yMax);
    }
  }
}
