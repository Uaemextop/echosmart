/**
 * EchoSmart Demo — Activity Log Page Renderer
 *
 * Displays a chronological feed of system events including
 * sensor readings, gateway status changes, user actions,
 * and configuration updates.
 *
 * @module pages/activity
 */

import { timeAgo } from "../js/modules/alerts.js";

/** @typedef {{ id: number, type: string, icon: string, message: string, detail: string, time: Date }} ActivityEvent */

let _nextId = 1;

/**
 * Event type metadata for display.
 * @type {Record<string, {icon: string, color: string}>}
 */
const EVENT_TYPES = {
  sensor:  { icon: "📡", color: "var(--green)" },
  alert:   { icon: "🔔", color: "var(--high)" },
  gateway: { icon: "📶", color: "var(--cyan)" },
  user:    { icon: "👤", color: "var(--text-secondary)" },
  system:  { icon: "⚙️", color: "var(--text-muted)" },
  config:  { icon: "🔧", color: "var(--light)" },
};

/**
 * Generate initial demo activity events.
 * @returns {ActivityEvent[]}
 */
function _generateEvents() {
  const now = Date.now();
  return [
    _event("sensor",  "Lectura de sensores completada",     "Todos los sensores reportan valores normales", now - 1 * 60000),
    _event("alert",   "Alerta de temperatura resuelta",     "DS18B20 #2 volvió al rango óptimo (24.8°C)",  now - 3 * 60000),
    _event("gateway", "Gateway-01 sincronización exitosa",  "Datos enviados al servidor cloud",             now - 5 * 60000),
    _event("user",    "María García inició sesión",         "Acceso desde 192.168.1.45",                    now - 12 * 60000),
    _event("system",  "Respaldo automático completado",     "Base de datos: 14.2 MB respaldados",           now - 18 * 60000),
    _event("sensor",  "Calibración de BH1750 completada",   "Luminosidad recalibrada correctamente",        now - 25 * 60000),
    _event("config",  "Umbrales de temperatura actualizados", "Nuevo rango: 18-28°C por Admin",             now - 35 * 60000),
    _event("alert",   "Nueva alerta: CO₂ elevado",         "MH-Z19C reporta 980 ppm en Zona A",            now - 45 * 60000),
    _event("gateway", "Gateway-03 reinicio programado",     "Reinicio preventivo completado (uptime: 7d)",   now - 60 * 60000),
    _event("user",    "John Doe modificó configuración",    "Intervalo de lectura: 30s → 15s",              now - 75 * 60000),
    _event("system",  "Actualización de firmware disponible", "Gateway-02: v2.4.1 → v2.5.0",                now - 90 * 60000),
    _event("sensor",  "Sensor Soil+ADS1115 reconectado",    "Zona B, humedad suelo: 65%",                   now - 120 * 60000),
    _event("config",  "Notificación por email activada",    "Configurado por Admin",                        now - 150 * 60000),
    _event("alert",   "Alerta de humedad de suelo",         "Soil #1: 38% — por debajo del umbral (50%)",   now - 180 * 60000),
    _event("gateway", "Gateway-01 conectado",               "3 sensores detectados, estado: online",         now - 240 * 60000),
  ];
}

/** Active filter state */
let _activeFilter = "all";

/**
 * Render the activity log page.
 */
export function renderActivity() {
  const container = document.getElementById("activityFeed");
  if (!container) return;

  const events = _generateEvents();
  _renderFeed(container, events);
  _bindFilterButtons(container, events);
}

/**
 * Render the activity feed content.
 * @param {HTMLElement} container
 * @param {ActivityEvent[]} events
 */
function _renderFeed(container, events) {
  const filtered = _activeFilter === "all"
    ? events
    : events.filter((e) => e.type === _activeFilter);

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="activity-empty">
        <span class="activity-empty__icon">📋</span>
        <span class="activity-empty__text">No hay eventos de este tipo</span>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map((event) => {
    const meta = EVENT_TYPES[event.type] || EVENT_TYPES.system;
    return `
      <div class="activity-item">
        <div class="activity-item__timeline">
          <span class="activity-item__dot" style="background: ${meta.color}"></span>
          <span class="activity-item__line"></span>
        </div>
        <div class="activity-item__content">
          <div class="activity-item__header">
            <span class="activity-item__icon">${meta.icon}</span>
            <span class="activity-item__message">${event.message}</span>
            <span class="activity-item__time">${timeAgo(event.time)}</span>
          </div>
          <span class="activity-item__detail">${event.detail}</span>
        </div>
      </div>
    `;
  }).join("");
}

/**
 * Bind filter tab buttons.
 * @param {HTMLElement} container
 * @param {ActivityEvent[]} events
 */
function _bindFilterButtons(container, events) {
  document.querySelectorAll(".activity-filter__btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".activity-filter__btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      _activeFilter = btn.dataset.filter;
      _renderFeed(container, events);
    });
  });
}

/**
 * Create an activity event.
 */
function _event(type, message, detail, ts) {
  return {
    id: _nextId++,
    type,
    icon: EVENT_TYPES[type]?.icon || "📌",
    message,
    detail,
    time: new Date(ts),
  };
}
