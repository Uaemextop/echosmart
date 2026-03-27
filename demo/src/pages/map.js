/**
 * EchoSmart Demo — Greenhouse Map Renderer
 *
 * Renders a Mexican rose greenhouse (invernadero) floor plan with:
 *  - Structural elements: columns, arched roof trusses, walls
 *  - Growing beds (camas) arranged in rows with aisles (pasillos)
 *  - Canvas-based heatmap with IDW interpolation clipped to greenhouse walls
 *  - 9 multi-parameter sensor nodes — every node reads ALL 5 parameters
 *  - Per-aisle average calculations and labels
 *  - Switchable parameter overlays (temperature, humidity, CO2, light, soil)
 *  - Color scale legend
 *
 * @module pages/map
 */

import { formatValue, getColors, getSpecs } from "../js/modules/sensors.js";

/* ===== Color Scale Configuration per Parameter ===== */

const COLOR_SCALES = {
  temperature: [
    [10, 66, 133, 244],
    [18, 0, 188, 212],
    [23, 0, 230, 118],
    [28, 255, 145, 0],
    [35, 255, 23, 68],
  ],
  humidity: [
    [20, 255, 145, 0],
    [50, 255, 235, 59],
    [60, 0, 230, 118],
    [80, 0, 188, 212],
    [99, 66, 133, 244],
  ],
  co2: [
    [350, 66, 133, 244],
    [400, 0, 230, 118],
    [700, 0, 188, 212],
    [1000, 255, 145, 0],
    [1500, 255, 23, 68],
  ],
  light: [
    [0, 33, 33, 66],
    [5000, 66, 133, 244],
    [10000, 0, 230, 118],
    [30000, 255, 235, 59],
    [50000, 255, 145, 0],
  ],
  soil: [
    [15, 255, 23, 68],
    [40, 255, 145, 0],
    [50, 0, 230, 118],
    [80, 0, 188, 212],
    [95, 66, 133, 244],
  ],
};

const PARAM_LABELS = {
  temperature: "Temperatura",
  humidity: "Humedad",
  co2: "CO\u2082",
  light: "Luminosidad",
  soil: "Humedad Suelo",
};

/* ===== Greenhouse Structure ===== */

const GH_W = 800;
const GH_H = 500;
const WALL_M = 30;

const NUM_BEDS = 6;
const BED_PAD_X = 50;
const BED_PAD_Y = 55;
const AISLE_W = 18;
const NUM_COLS_STRUCT = 7;

function computeBeds() {
  const innerW = GH_W - 2 * WALL_M - 2 * BED_PAD_X;
  const totalAisle = (NUM_BEDS - 1) * AISLE_W;
  const bedW = (innerW - totalAisle) / NUM_BEDS;
  const bedY = WALL_M + BED_PAD_Y;
  const bedH = GH_H - 2 * WALL_M - 2 * BED_PAD_Y;
  const beds = [];
  for (let i = 0; i < NUM_BEDS; i++) {
    beds.push({
      x: WALL_M + BED_PAD_X + i * (bedW + AISLE_W),
      y: bedY, w: bedW, h: bedH,
      label: "Cama " + (i + 1),
    });
  }
  return beds;
}

function computeColumnYs() {
  const ys = [];
  const inner = GH_H - 2 * WALL_M;
  for (let i = 0; i <= NUM_COLS_STRUCT; i++) {
    ys.push(WALL_M + (i / NUM_COLS_STRUCT) * inner);
  }
  return ys;
}

/* ===== Aisle Zones (for per-aisle averages) ===== */

function computeAisles() {
  const beds = computeBeds();
  const aisles = [];
  /* Left side aisle */
  aisles.push({
    label: "Pasillo Izq",
    x: WALL_M, y: WALL_M,
    w: beds[0].x - WALL_M,
    h: GH_H - 2 * WALL_M,
    cx: (WALL_M + beds[0].x) / 2,
    cy: GH_H / 2,
  });
  /* Aisles between beds */
  for (let i = 0; i < NUM_BEDS - 1; i++) {
    const ax = beds[i].x + beds[i].w;
    aisles.push({
      label: "Pasillo " + (i + 1),
      x: ax, y: WALL_M,
      w: AISLE_W,
      h: GH_H - 2 * WALL_M,
      cx: ax + AISLE_W / 2,
      cy: GH_H / 2,
    });
  }
  /* Right side aisle */
  const lastBed = beds[beds.length - 1];
  aisles.push({
    label: "Pasillo Der",
    x: lastBed.x + lastBed.w, y: WALL_M,
    w: GH_W - WALL_M - (lastBed.x + lastBed.w),
    h: GH_H - 2 * WALL_M,
    cx: (lastBed.x + lastBed.w + GH_W - WALL_M) / 2,
    cy: GH_H / 2,
  });
  return aisles;
}

/* ===== Sensor Nodes — Each reads ALL parameters ===== */

/*
 * 9 sensors in 3 rows × 3 columns distributed across the greenhouse.
 * Each sensor has per-parameter offsets to create realistic spatial variation.
 * All nodes contribute to EVERY parameter's heatmap.
 */
const SENSOR_NODES = [
  { id: "s1", x: 130, y: 400, name: "Sensor A1", aisle: 0,
    offsets: { temperature: 0, humidity: 0, co2: 0, light: 0, soil: 0 } },
  { id: "s2", x: 400, y: 400, name: "Sensor A2", aisle: 2,
    offsets: { temperature: 0.8, humidity: -2, co2: 15, light: 500, soil: -3 } },
  { id: "s3", x: 670, y: 400, name: "Sensor A3", aisle: 4,
    offsets: { temperature: -0.5, humidity: 3, co2: -20, light: -800, soil: 2 } },
  { id: "s4", x: 130, y: 250, name: "Sensor B1", aisle: 0,
    offsets: { temperature: 1.8, humidity: -5, co2: 30, light: 2000, soil: -5 } },
  { id: "s5", x: 400, y: 250, name: "Sensor B2", aisle: 2,
    offsets: { temperature: 2.5, humidity: -8, co2: 50, light: 4000, soil: -8 } },
  { id: "s6", x: 670, y: 250, name: "Sensor B3", aisle: 4,
    offsets: { temperature: 1.2, humidity: -3, co2: 25, light: 1500, soil: -4 } },
  { id: "s7", x: 130, y: 100, name: "Sensor C1", aisle: 0,
    offsets: { temperature: -1.2, humidity: 5, co2: -10, light: -2000, soil: 4 } },
  { id: "s8", x: 400, y: 100, name: "Sensor C2", aisle: 2,
    offsets: { temperature: -0.3, humidity: 3, co2: -5, light: -500, soil: 2 } },
  { id: "s9", x: 670, y: 100, name: "Sensor C3", aisle: 4,
    offsets: { temperature: -1.8, humidity: 7, co2: -25, light: -3000, soil: 6 } },
];

/** Get the value of a specific parameter at a sensor node */
function getNodeValue(node, paramKey, sensors) {
  if (!sensors || !sensors[paramKey]) return 0;
  return sensors[paramKey].value + (node.offsets[paramKey] || 0);
}

/* ===== Heatmap ===== */

const HEATMAP_RES = 8;

function interpolateColor(value, scale) {
  if (value <= scale[0][0]) return [scale[0][1], scale[0][2], scale[0][3]];
  const last = scale[scale.length - 1];
  if (value >= last[0]) return [last[1], last[2], last[3]];
  for (let i = 0; i < scale.length - 1; i++) {
    const [v0, r0, g0, b0] = scale[i];
    const [v1, r1, g1, b1] = scale[i + 1];
    if (value >= v0 && value <= v1) {
      const t = (value - v0) / (v1 - v0);
      return [
        Math.round(r0 + t * (r1 - r0)),
        Math.round(g0 + t * (g1 - g0)),
        Math.round(b0 + t * (b1 - b0)),
      ];
    }
  }
  return [0, 0, 0];
}

function idwInterpolate(px, py, nodes) {
  const POWER = 2.5;
  let num = 0, den = 0;
  for (const n of nodes) {
    const d = Math.sqrt((px - n.x) ** 2 + (py - n.y) ** 2);
    if (d < 1) return n.value;
    const w = 1 / Math.pow(d, POWER);
    num += w * n.value;
    den += w;
  }
  return den > 0 ? num / den : 0;
}

/* ===== State ===== */

let activeParam = "temperature";
let canvasEl = null;
let sensorValues = {};

/* ===== Build SVG Structure ===== */

function buildStructureSVG() {
  const beds = computeBeds();
  const colYs = computeColumnYs();
  let svg = "";

  /* Roof arches */
  for (let i = 0; i <= 2; i++) {
    const cx = WALL_M + (i / 2) * (GH_W - 2 * WALL_M);
    svg += '<path d="M' + WALL_M + " " + WALL_M + " Q" + cx + " 10 " + (GH_W - WALL_M) + " " + WALL_M + '" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1.5"/>';
  }

  /* Walls */
  svg += '<rect x="' + WALL_M + '" y="' + WALL_M + '" width="' + (GH_W - 2 * WALL_M) + '" height="' + (GH_H - 2 * WALL_M) + '" rx="4" fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>';

  /* Columns */
  const colXs = [WALL_M + 5, GH_W / 2, GH_W - WALL_M - 5];
  for (const cx of colXs) {
    for (const cy of colYs) {
      svg += '<rect x="' + (cx - 4) + '" y="' + (cy - 4) + '" width="8" height="8" rx="1" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.15)" stroke-width="0.8"/>';
    }
  }

  /* Beds with rose plants */
  for (const b of beds) {
    svg += '<rect x="' + b.x + '" y="' + b.y + '" width="' + b.w + '" height="' + b.h + '" rx="3" fill="rgba(0,230,118,0.04)" stroke="rgba(0,230,118,0.12)" stroke-width="0.8" stroke-dasharray="4 3"/>';
    const np = Math.floor(b.h / 28);
    for (let p = 0; p < np; p++) {
      const py = b.y + 14 + p * (b.h - 28) / (np - 1);
      svg += '<circle cx="' + (b.x + b.w * 0.3) + '" cy="' + py + '" r="3" fill="rgba(0,230,118,0.08)" stroke="rgba(0,230,118,0.15)" stroke-width="0.5"/>';
      svg += '<circle cx="' + (b.x + b.w * 0.7) + '" cy="' + py + '" r="3" fill="rgba(0,230,118,0.08)" stroke="rgba(0,230,118,0.15)" stroke-width="0.5"/>';
    }
    svg += '<text x="' + (b.x + b.w / 2) + '" y="' + (b.y - 6) + '" text-anchor="middle" fill="rgba(255,255,255,0.25)" font-size="9" font-weight="600">' + b.label + '</text>';
  }

  /* Aisle labels */
  for (let i = 0; i < NUM_BEDS - 1; i++) {
    const ax = beds[i].x + beds[i].w + AISLE_W / 2;
    svg += '<text x="' + ax + '" y="' + (GH_H - WALL_M - 8) + '" text-anchor="middle" fill="rgba(255,255,255,0.15)" font-size="7" transform="rotate(-90,' + ax + ',' + (GH_H - WALL_M - 8) + ')">Pasillo ' + (i + 1) + '</text>';
  }

  /* Door */
  const dx = GH_W / 2 - 30;
  svg += '<rect x="' + dx + '" y="' + (GH_H - WALL_M - 2) + '" width="60" height="6" rx="2" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>';
  svg += '<text x="' + (GH_W / 2) + '" y="' + (GH_H - WALL_M + 14) + '" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-size="9">Entrada</text>';

  /* Ventilation */
  svg += '<text x="' + (WALL_M + 10) + '" y="' + (WALL_M - 5) + '" fill="rgba(255,255,255,0.2)" font-size="8">\u25BD Ventilaci\u00f3n cenital</text>';

  return '<svg class="greenhouse-svg" viewBox="0 0 ' + GH_W + " " + GH_H + '" preserveAspectRatio="xMidYMid meet">' + svg + "</svg>";
}

/* ===== Heatmap Drawing (clipped to greenhouse walls) ===== */

function drawHeatmap(paramKey, sensors) {
  if (!canvasEl) return;
  const ctx = canvasEl.getContext("2d");
  const cw = canvasEl.width;
  const ch = canvasEl.height;
  const scale = COLOR_SCALES[paramKey];
  if (!scale) return;

  /* Clear entire canvas to transparent */
  ctx.clearRect(0, 0, cw, ch);

  /* Build interpolation nodes — ALL sensors provide data for every parameter */
  const nodes = SENSOR_NODES.map(function (n) {
    return {
      x: (n.x / GH_W) * cw,
      y: (n.y / GH_H) * ch,
      value: getNodeValue(n, paramKey, sensors),
    };
  });

  /* Greenhouse wall boundaries in canvas pixels */
  const wallL = Math.floor((WALL_M / GH_W) * cw);
  const wallT = Math.floor((WALL_M / GH_H) * ch);
  const wallR = Math.ceil(((GH_W - WALL_M) / GH_W) * cw);
  const wallB = Math.ceil(((GH_H - WALL_M) / GH_H) * ch);

  const imgData = ctx.createImageData(cw, ch);
  const data = imgData.data;
  for (let py = 0; py < ch; py += HEATMAP_RES) {
    for (let px = 0; px < cw; px += HEATMAP_RES) {
      /* Only draw INSIDE the greenhouse walls */
      if (px < wallL || px >= wallR || py < wallT || py >= wallB) continue;
      const val = idwInterpolate(px, py, nodes);
      const c = interpolateColor(val, scale);
      for (let dy = 0; dy < HEATMAP_RES && (py + dy) < ch; dy++) {
        for (let dx = 0; dx < HEATMAP_RES && (px + dx) < cw; dx++) {
          const idx = ((py + dy) * cw + (px + dx)) * 4;
          data[idx] = c[0];
          data[idx + 1] = c[1];
          data[idx + 2] = c[2];
          data[idx + 3] = 85;
        }
      }
    }
  }
  ctx.putImageData(imgData, 0, 0);
}

/* ===== Sensor Pins ===== */

function buildSensorPins(sensors) {
  const COLORS = getColors();
  return SENSOR_NODES.map(function (node) {
    const leftPct = (node.x / GH_W) * 100;
    const topPct = (node.y / GH_H) * 100;
    const val = getNodeValue(node, activeParam, sensors);
    const color = COLORS[activeParam] || "#00E676";
    return '<div class="greenhouse-sensor-pin" style="left:' + leftPct + '%;top:' + topPct + '%;" data-sensor-id="' + node.id + '">' +
      '<div class="greenhouse-sensor-pin__dot" style="background:' + color + '"></div>' +
      '<div class="greenhouse-sensor-pin__tooltip"><strong>' + node.name + '</strong><br/>' + formatValue(activeParam, val) + '</div></div>';
  }).join("");
}

/* ===== Legend ===== */

function buildLegend(paramKey) {
  const scale = COLOR_SCALES[paramKey];
  const spec = getSpecs()[paramKey];
  const label = PARAM_LABELS[paramKey] || paramKey;
  const stops = scale.map(function (s, i) {
    return "rgb(" + s[1] + "," + s[2] + "," + s[3] + ") " + ((i / (scale.length - 1)) * 100) + "%";
  }).join(", ");
  const labels = scale.map(function (s) { return "<span>" + s[0] + spec.unit + "</span>"; }).join("");
  return '<div class="greenhouse-legend">' +
    '<span class="greenhouse-legend__title">' + label + '</span>' +
    '<div class="greenhouse-legend__bar" style="background:linear-gradient(to right, ' + stops + ')"></div>' +
    '<div class="greenhouse-legend__labels">' + labels + '</div>' +
    '<div class="greenhouse-legend__optimal">\u00d3ptimo: ' + spec.optMin + '\u2013' + spec.optMax + spec.unit + '</div></div>';
}

/* ===== Parameter Selector ===== */

function buildParamSelector() {
  const params = Object.keys(COLOR_SCALES);
  let html = '<div class="greenhouse-param-selector">';
  for (let i = 0; i < params.length; i++) {
    const p = params[i];
    const cls = p === activeParam ? "greenhouse-param-btn greenhouse-param-btn--active" : "greenhouse-param-btn";
    html += '<button class="' + cls + '" data-param="' + p + '">' + PARAM_LABELS[p] + '</button>';
  }
  html += '</div>';
  return html;
}

/* ===== Isotherm Labels at Sensor Positions ===== */

function buildIsotherms(sensors) {
  if (!sensors) return "";
  const scale = COLOR_SCALES[activeParam];
  return SENSOR_NODES.map(function (node) {
    const val = getNodeValue(node, activeParam, sensors);
    const left = (node.x / GH_W) * 100;
    const top = (node.y / GH_H) * 100;
    const c = interpolateColor(val, scale);
    return '<div class="greenhouse-isotherm" style="left:' + left + '%;top:' + (top + 3) + '%;">' +
      '<span style="color:rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')">' + formatValue(activeParam, val) + '</span></div>';
  }).join("");
}

/* ===== Per-Aisle Average Calculation ===== */

/**
 * Compute per-aisle averages using IDW interpolation.
 * Samples multiple points along each aisle and averages the IDW-interpolated
 * values, giving accurate spatial representation of sensor readings.
 */
function computeAisleAverages(paramKey, sensors) {
  if (!sensors) return [];
  const aisles = computeAisles();
  const SAMPLE_COUNT = 5;

  /* Build IDW nodes from all sensors */
  const nodes = SENSOR_NODES.map(function (n) {
    return { x: n.x, y: n.y, value: getNodeValue(n, paramKey, sensors) };
  });

  return aisles.map(function (aisle) {
    let sum = 0;
    /* Sample points vertically along the aisle center */
    for (let s = 0; s < SAMPLE_COUNT; s++) {
      const sampleY = WALL_M + ((s + 0.5) / SAMPLE_COUNT) * (GH_H - 2 * WALL_M);
      sum += idwInterpolate(aisle.cx, sampleY, nodes);
    }
    return {
      label: aisle.label,
      cx: aisle.cx,
      cy: aisle.cy,
      avg: sum / SAMPLE_COUNT,
    };
  });
}

function buildAisleAverages(sensors) {
  if (!sensors) return "";
  const avgs = computeAisleAverages(activeParam, sensors);
  const scale = COLOR_SCALES[activeParam];
  const spec = getSpecs()[activeParam];
  let html = "";
  for (let i = 0; i < avgs.length; i++) {
    const a = avgs[i];
    const left = (a.cx / GH_W) * 100;
    const top = ((WALL_M + 20) / GH_H) * 100;
    const c = interpolateColor(a.avg, scale);
    const valStr = spec.decimals > 0
      ? a.avg.toFixed(spec.decimals) + spec.unit
      : Math.round(a.avg) + spec.unit;
    html += '<div class="greenhouse-aisle-avg" style="left:' + left + '%;top:' + top + '%;">' +
      '<div class="greenhouse-aisle-avg__label">' + a.label + '</div>' +
      '<div class="greenhouse-aisle-avg__value" style="color:rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')">Prom: ' + valStr + '</div>' +
      '</div>';
  }
  return html;
}

/* ===== Public API ===== */

export function renderMap(sensors) {
  const container = document.getElementById("mapPins");
  if (!container) return;

  const placeholder = container.parentElement ? container.parentElement.querySelector(".map-placeholder") : null;
  if (placeholder) placeholder.style.display = "none";

  sensorValues = sensors;

  container.innerHTML =
    '<div class="greenhouse-layout">' +
    '<canvas id="heatmapCanvas" class="greenhouse-heatmap-canvas"></canvas>' +
    buildStructureSVG() +
    buildSensorPins(sensors) +
    buildIsotherms(sensors) +
    buildAisleAverages(sensors) +
    buildParamSelector() +
    buildLegend(activeParam) +
    '</div>';

  canvasEl = document.getElementById("heatmapCanvas");
  if (canvasEl) {
    const rect = canvasEl.parentElement.getBoundingClientRect();
    canvasEl.width = Math.floor(rect.width);
    canvasEl.height = Math.floor(rect.height);
    drawHeatmap(activeParam, sensors);
  }

  container.querySelectorAll(".greenhouse-param-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeParam = btn.dataset.param;
      renderMap(sensorValues);
    });
  });
}

export function updateMap(sensors) {
  if (!sensors) return;
  sensorValues = sensors;

  if (canvasEl) {
    drawHeatmap(activeParam, sensors);
  }

  /* Update sensor pin tooltips */
  SENSOR_NODES.forEach(function (node) {
    const pinEl = document.querySelector('[data-sensor-id="' + node.id + '"] .greenhouse-sensor-pin__tooltip');
    if (pinEl) {
      const val = getNodeValue(node, activeParam, sensors);
      pinEl.innerHTML = "<strong>" + node.name + "</strong><br/>" + formatValue(activeParam, val);
    }
  });

  /* Refresh isotherms */
  const container = document.getElementById("mapPins");
  if (container) {
    container.querySelectorAll(".greenhouse-isotherm").forEach(function (el) { el.remove(); });
    container.querySelectorAll(".greenhouse-aisle-avg").forEach(function (el) { el.remove(); });
    const layout = container.querySelector(".greenhouse-layout");
    if (layout) {
      layout.insertAdjacentHTML("beforeend", buildIsotherms(sensors));
      layout.insertAdjacentHTML("beforeend", buildAisleAverages(sensors));
    }
  }
}
