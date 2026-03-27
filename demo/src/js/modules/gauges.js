/**
 * EchoSmart Demo — Gauge Chart Renderer
 *
 * Draws semicircular gauge charts on Canvas elements,
 * showing current value relative to optimal and total ranges.
 *
 * @module gauges
 */

/** Visual constants for gauge rendering */
const GAUGE_HEIGHT = 110;
const ARC_WIDTH = 12;
const MAX_RADIUS = 80;
const PADDING = 10;

/** Color tokens */
const BG_ARC_COLOR = "rgba(255,255,255,0.06)";
const OPTIMAL_ARC_COLOR = "rgba(0,230,118,0.2)";
const VALUE_TEXT_COLOR = "#E0E0E0";
const LABEL_TEXT_COLOR = "#546e7a";
const OPTIMAL_LABEL_COLOR = "#00E676";

/** Font definitions */
const FONT_VALUE = "bold 18px -apple-system, sans-serif";
const FONT_LABEL = "10px -apple-system, sans-serif";
const FONT_OPTIMAL = "9px -apple-system, sans-serif";

/**
 * Draw a gauge chart on a canvas element.
 *
 * @param {string} canvasId  — DOM id of the target canvas
 * @param {number} value     — Current sensor value
 * @param {number} min       — Sensor minimum
 * @param {number} max       — Sensor maximum
 * @param {number} optMin    — Optimal range minimum
 * @param {number} optMax    — Optimal range maximum
 * @param {string} color     — Accent color for the value arc
 * @param {string} unit      — Display unit suffix
 */
export function drawGauge(canvasId, value, min, max, optMin, optMax, color, unit) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.width = canvas.parentElement.offsetWidth || 160;
  const h = canvas.height = GAUGE_HEIGHT;
  const cx = w / 2;
  const cy = h - PADDING;
  const r = Math.min(w / 2 - PADDING, MAX_RADIUS);

  ctx.clearRect(0, 0, w, h);

  _drawBackgroundArc(ctx, cx, cy, r);
  _drawOptimalArc(ctx, cx, cy, r, min, max, optMin, optMax);
  _drawValueArc(ctx, cx, cy, r, min, max, value, color);
  _drawValueText(ctx, cx, cy, value, unit);
  _drawRangeLabels(ctx, cx, cy, r, min, max, unit);
  _drawOptimalLabel(ctx, cx, cy, optMin, optMax);
}

/* ---- Private drawing helpers ---- */

function _drawBackgroundArc(ctx, cx, cy, r) {
  ctx.beginPath();
  ctx.arc(cx, cy, r, Math.PI, 0, false);
  ctx.lineWidth = ARC_WIDTH;
  ctx.strokeStyle = BG_ARC_COLOR;
  ctx.stroke();
}

function _drawOptimalArc(ctx, cx, cy, r, min, max, optMin, optMax) {
  const range = max - min;
  const optStart = Math.PI + ((optMin - min) / range) * Math.PI;
  const optEnd = Math.PI + ((optMax - min) / range) * Math.PI;

  ctx.beginPath();
  ctx.arc(cx, cy, r, optStart, optEnd, false);
  ctx.lineWidth = ARC_WIDTH;
  ctx.strokeStyle = OPTIMAL_ARC_COLOR;
  ctx.stroke();
}

function _drawValueArc(ctx, cx, cy, r, min, max, value, color) {
  const normalized = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const valueAngle = Math.PI + normalized * Math.PI;

  ctx.beginPath();
  ctx.arc(cx, cy, r, Math.PI, valueAngle, false);
  ctx.lineWidth = ARC_WIDTH;
  ctx.lineCap = "round";
  ctx.strokeStyle = color;
  ctx.stroke();
}

function _drawValueText(ctx, cx, cy, value, unit) {
  ctx.fillStyle = VALUE_TEXT_COLOR;
  ctx.font = FONT_VALUE;
  ctx.textAlign = "center";
  ctx.fillText(value.toFixed(1) + unit, cx, cy - 20);
}

function _drawRangeLabels(ctx, cx, cy, r, min, max, unit) {
  ctx.fillStyle = LABEL_TEXT_COLOR;
  ctx.font = FONT_LABEL;

  ctx.textAlign = "left";
  ctx.fillText(min + unit, cx - r - 5, cy + 14);

  ctx.textAlign = "right";
  ctx.fillText(max + unit, cx + r + 5, cy + 14);
}

function _drawOptimalLabel(ctx, cx, cy, optMin, optMax) {
  ctx.fillStyle = OPTIMAL_LABEL_COLOR;
  ctx.font = FONT_OPTIMAL;
  ctx.textAlign = "center";
  ctx.fillText(`Óptimo: ${optMin}–${optMax}`, cx, cy + 2);
}
