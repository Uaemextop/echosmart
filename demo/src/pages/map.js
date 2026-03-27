/**
 * EchoSmart Demo — Map Page Renderer
 *
 * Renders an interactive greenhouse floor-plan with temperature-based
 * heatmap coloring per zone and overlaid sensor readings.
 */

import { ICONS } from "../js/modules/icons.js";
import { formatValue, getColors } from "../js/modules/sensors.js";

/** Temperature thresholds for color mapping (°C) */
const TEMP_COLD = 14;
const TEMP_COOL = 18;
const TEMP_OPT_HIGH = 26;
const TEMP_WARM = 28;
const TEMP_HOT = 35;

/** Default temperature when sensor data is not available */
const DEFAULT_TEMPERATURE = 24;

/**
 * Map a temperature value to a CSS color.
 * Blue (cold) → Green (optimal) → Red (hot)
 */
function tempToColor(temp) {
  let r, g, b;

  if (temp <= TEMP_COLD) {
    r = 66; g = 133; b = 244;           // blue
  } else if (temp <= TEMP_COOL) {
    const t = (temp - TEMP_COLD) / (TEMP_COOL - TEMP_COLD);
    r = Math.round(66 + t * (0 - 66));
    g = Math.round(133 + t * (188 - 133));
    b = Math.round(244 + t * (212 - 244));
  } else if (temp <= TEMP_OPT_HIGH) {
    const t = (temp - TEMP_COOL) / (TEMP_OPT_HIGH - TEMP_COOL);
    r = Math.round(0 + t * (0));
    g = Math.round(188 + t * (230 - 188));
    b = Math.round(212 + t * (118 - 212));
  } else if (temp <= TEMP_WARM) {
    const t = (temp - TEMP_OPT_HIGH) / (TEMP_WARM - TEMP_OPT_HIGH);
    r = Math.round(0 + t * 255);
    g = Math.round(230 - t * 85);
    b = Math.round(118 - t * 118);
  } else if (temp <= TEMP_HOT) {
    const t = Math.min((temp - TEMP_WARM) / (TEMP_HOT - TEMP_WARM), 1);
    r = 255;
    g = Math.round(145 - t * 123);
    b = Math.round(0 + t * 68);
  } else {
    r = 255; g = 23; b = 68;            // critical red
  }
  return `rgb(${r},${g},${b})`;
}

/**
 * Zone definitions for the greenhouse floor plan.
 * Each zone has percentage-based position/size within the map container.
 */
const ZONES = [
  {
    id: "zona-a", label: "Zona A", sensorKey: "temperature",
    x: "2%", y: "8%", w: "46%", h: "42%",
    sensors: [
      { key: "temperature", name: "DS18B20 #1", x: "25%", y: "30%" },
      { key: "humidity",    name: "DHT22 #1",   x: "70%", y: "60%" },
      { key: "co2",         name: "MH-Z19C",    x: "25%", y: "70%" },
    ],
  },
  {
    id: "zona-b", label: "Zona B", sensorKey: "temperature",
    x: "52%", y: "8%", w: "46%", h: "84%",
    sensors: [
      { key: "light", name: "BH1750",       x: "50%", y: "20%" },
      { key: "soil",  name: "Soil+ADS1115", x: "50%", y: "50%" },
      { key: "co2",   name: "MH-Z19C #2",   x: "50%", y: "80%" },
    ],
  },
  {
    id: "zona-c", label: "Zona C", sensorKey: "temperature",
    x: "2%", y: "54%", w: "46%", h: "38%",
    sensors: [
      { key: "temperature", name: "DS18B20 #2", x: "30%", y: "40%" },
      { key: "humidity",    name: "DHT22 #2",   x: "70%", y: "40%" },
    ],
  },
];

/* Temperature offsets per zone so each shows a different temp */
const ZONE_TEMP_OFFSETS = { "zona-a": 0, "zona-b": 1.5, "zona-c": -1.2 };

let rendered = false;

export function renderMap(sensors) {
  rendered = true;

  const container = document.getElementById("mapPins");
  if (!container) return;

  /* Hide the placeholder */
  const placeholder = container.parentElement?.querySelector(".map-placeholder");
  if (placeholder) placeholder.style.display = "none";

  const baseTemp = sensors ? sensors.temperature.value : DEFAULT_TEMPERATURE;

  container.innerHTML = `
    <div class="greenhouse-layout">
      <!-- Greenhouse outer walls -->
      <svg class="greenhouse-svg" viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet">
        <!-- Roof -->
        <path d="M20 80 L300 15 L580 80" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2"/>
        <path d="M20 80 L20 380 L580 380 L580 80 Z" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1.5" stroke-dasharray="6 3"/>
        <!-- Internal dividers -->
        <line x1="300" y1="80" x2="300" y2="380" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="4 4"/>
        <line x1="20" y1="230" x2="300" y2="230" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="4 4"/>
        <!-- Door -->
        <rect x="135" y="370" width="50" height="10" rx="2" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
        <text x="160" y="395" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-size="10">Entrada</text>
        <!-- Plant row hints -->
        ${generatePlantRows()}
      </svg>

      ${ZONES.map((zone) => {
        const temp = baseTemp + (ZONE_TEMP_OFFSETS[zone.id] || 0);
        const color = tempToColor(temp);
        return `
        <div class="greenhouse-zone" id="${zone.id}"
             style="left:${zone.x};top:${zone.y};width:${zone.w};height:${zone.h};
                    background:${color};opacity:0.18;">
        </div>
        <div class="greenhouse-zone-label" style="left:calc(${zone.x} + 8px);top:calc(${zone.y} + 6px);">
          <span class="greenhouse-zone-label__name">${zone.label}</span>
          <span class="greenhouse-zone-label__temp" id="${zone.id}-temp">${temp.toFixed(1)}°C</span>
        </div>
        ${zone.sensors.map((s) => {
          const sVal = sensors ? sensors[s.key].value : 0;
          const zoneLeft = parseFloat(zone.x);
          const zoneTop = parseFloat(zone.y);
          const zoneW = parseFloat(zone.w);
          const zoneH = parseFloat(zone.h);
          const pinLeft = zoneLeft + (parseFloat(s.x) / 100) * zoneW;
          const pinTop = zoneTop + (parseFloat(s.y) / 100) * zoneH;
          return `
          <div class="greenhouse-sensor-pin" style="left:${pinLeft}%;top:${pinTop}%;">
            <div class="greenhouse-sensor-pin__dot" style="background:${getColors()[s.key]}"></div>
            <div class="greenhouse-sensor-pin__tooltip">
              <strong>${s.name}</strong><br/>
              ${formatValue(s.key, sVal)}
            </div>
          </div>`;
        }).join("")}
      `;
      }).join("")}
    </div>

    <!-- Temperature Legend -->
    <div class="greenhouse-legend">
      <span class="greenhouse-legend__title">Temperatura</span>
      <div class="greenhouse-legend__bar"></div>
      <div class="greenhouse-legend__labels">
        <span>14°C</span>
        <span>18°C</span>
        <span>23°C</span>
        <span>28°C</span>
        <span>35°C</span>
      </div>
    </div>
  `;
}

/** Plant row layout configuration per zone */
const PLANT_ROWS = {
  zoneA: { count: 3, startY: 110, spacing: 35, x1: 40, x2: 280 },
  zoneC: { count: 2, startY: 260, spacing: 40, x1: 40, x2: 280 },
  zoneB: { count: 5, startY: 110, spacing: 50, x1: 320, x2: 560 },
};

function generatePlantRows() {
  let rows = "";
  for (const zone of Object.values(PLANT_ROWS)) {
    for (let i = 0; i < zone.count; i++) {
      const y = zone.startY + i * zone.spacing;
      rows += `<line x1="${zone.x1}" y1="${y}" x2="${zone.x2}" y2="${y}" stroke="rgba(0,230,118,0.08)" stroke-width="8" stroke-linecap="round"/>`;
    }
  }
  return rows;
}

export function updateMap(sensors) {
  if (!sensors) return;
  const baseTemp = sensors.temperature.value;

  ZONES.forEach((zone) => {
    const temp = baseTemp + (ZONE_TEMP_OFFSETS[zone.id] || 0);
    const color = tempToColor(temp);
    const zoneEl = document.getElementById(zone.id);
    if (zoneEl) {
      zoneEl.style.background = color;
    }
    const tempLabel = document.getElementById(zone.id + "-temp");
    if (tempLabel) {
      tempLabel.textContent = temp.toFixed(1) + "°C";
    }
  });
}
