/**
 * EchoSmart Demo — Application Entry Point
 *
 * Wires together all modules: router, sensors, alerts, gateway, pages.
 */

/* ---- CSS imports (Vite handles bundling) ---- */
import "./css/variables.css";
import "./css/base.css";
import "./css/sidebar.css";
import "./css/layout.css";
import "./css/components.css";
import "./css/dashboard.css";
import "./css/sensors-page.css";
import "./css/alerts-page.css";
import "./css/map-page.css";
import "./css/reports-page.css";
import "./css/settings-page.css";
import "./css/users-page.css";
import "./css/utilities.css";

/* ---- Module imports ---- */
import { createSensors, tickSensors } from "./js/modules/sensors.js";
import { createInitialAlerts, evaluateAlerts, activeCount } from "./js/modules/alerts.js";
import { tickGateways } from "./js/modules/gateway.js";
import { initRouter } from "./js/modules/router.js";

/* ---- Page renderers ---- */
import { renderDashboard, updateDashboard } from "./pages/dashboard.js";
import { renderSensors, updateSensors } from "./pages/sensors.js";
import { renderAlerts } from "./pages/alerts.js";
import { renderSettings } from "./pages/settings.js";
import { renderReports } from "./pages/reports.js";
import { renderMap, updateMap } from "./pages/map.js";
import { renderUsers } from "./pages/users.js";

/* ---- State ---- */
const sensors = createSensors();
const alerts = createInitialAlerts();

/* ---- Clock ---- */
function updateClock() {
  const el = document.getElementById("clock");
  if (!el) return;
  const now = new Date();
  el.textContent =
    now.getHours().toString().padStart(2, "0") + ":" +
    now.getMinutes().toString().padStart(2, "0") + ":" +
    now.getSeconds().toString().padStart(2, "0");
}

/* ---- Badge updater ---- */
function updateBadge() {
  const badge = document.getElementById("alertBadge");
  if (badge) {
    const count = activeCount(alerts);
    badge.textContent = count;
    badge.style.display = count > 0 ? "" : "none";
  }
}

/* ---- Mobile sidebar ---- */
function initMobileSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const menuBtn = document.getElementById("mobileMenuBtn");

  function open() {
    sidebar?.classList.add("open");
    overlay?.classList.add("active");
  }

  function close() {
    sidebar?.classList.remove("open");
    overlay?.classList.remove("active");
  }

  menuBtn?.addEventListener("click", open);
  overlay?.addEventListener("click", close);

  /* Close sidebar on nav click (mobile) */
  document.querySelectorAll(".sidebar__link").forEach((link) => {
    link.addEventListener("click", close);
  });
}

/* ---- Init ---- */
document.addEventListener("DOMContentLoaded", () => {
  initMobileSidebar();
  updateClock();
  setInterval(updateClock, 1000);

  /* Router setup */
  initRouter({
    dashboard: () => renderDashboard(sensors, alerts),
    sensors:   () => renderSensors(sensors),
    alerts:    () => renderAlerts(alerts),
    settings:  () => renderSettings(),
    reports:   () => renderReports(sensors),
    map:       () => renderMap(sensors),
    users:     () => renderUsers(),
  }, "dashboard");

  updateBadge();

  /* Live tick — every 3 seconds */
  setInterval(() => {
    tickSensors(sensors);
    tickGateways(3000);
    evaluateAlerts(sensors, alerts);
    updateBadge();

    /* Update the currently visible page */
    const hash = location.hash.replace("#", "") || "dashboard";
    if (hash === "dashboard") updateDashboard(sensors, alerts);
    if (hash === "sensors")   updateSensors(sensors);
    if (hash === "alerts")    renderAlerts(alerts);
    if (hash === "map")       updateMap(sensors);
  }, 3000);
});
