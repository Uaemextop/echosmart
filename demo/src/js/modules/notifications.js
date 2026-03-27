/**
 * EchoSmart Demo — Notifications Module
 *
 * Manages the notification dropdown panel in the topbar.
 * Displays recent alerts with severity indicators and relative timestamps.
 *
 * @module modules/notifications
 */

import { timeAgo } from "./alerts.js";

/** Whether the dropdown event listeners have been bound */
let _bound = false;

/** @type {HTMLElement|null} */
let _dropdown = null;

/**
 * Severity metadata for display.
 * @type {Record<string, {label: string, icon: string}>}
 */
const SEVERITY_META = {
  critical: { label: "Crítico", icon: "🔴" },
  high:     { label: "Alto",    icon: "🟠" },
  medium:   { label: "Medio",   icon: "🟡" },
  low:      { label: "Bajo",    icon: "🔵" },
};

/**
 * Initialise the notification dropdown on the topbar bell button.
 * Idempotent — safe to call multiple times.
 *
 * @param {import("./alerts.js").Alert[]} alerts
 */
export function initNotifications(alerts) {
  if (_bound) return;
  _bound = true;

  _createDropdownElement();

  const bellBtn = document.querySelector(".topbar__btn[aria-label='Notificaciones']");
  if (!bellBtn) return;

  bellBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    _toggleDropdown(alerts);
  });

  document.addEventListener("click", (e) => {
    if (_dropdown && !_dropdown.contains(e.target)) {
      _closeDropdown();
    }
  });
}

/**
 * Update the notification dropdown content if it's open.
 * @param {import("./alerts.js").Alert[]} alerts
 */
export function updateNotifications(alerts) {
  if (_dropdown && _dropdown.classList.contains("notifications--open")) {
    _renderContent(alerts);
  }
}

/* ===== Private helpers ===== */

function _createDropdownElement() {
  _dropdown = document.createElement("div");
  _dropdown.className = "notifications";
  _dropdown.id = "notificationsDropdown";

  const topbar = document.querySelector(".topbar__actions");
  if (topbar) {
    topbar.style.position = "relative";
    topbar.appendChild(_dropdown);
  }
}

function _toggleDropdown(alerts) {
  if (!_dropdown) return;

  if (_dropdown.classList.contains("notifications--open")) {
    _closeDropdown();
  } else {
    _renderContent(alerts);
    _dropdown.classList.add("notifications--open");
  }
}

function _closeDropdown() {
  if (_dropdown) {
    _dropdown.classList.remove("notifications--open");
  }
}

function _renderContent(alerts) {
  if (!_dropdown) return;

  const recent = alerts.slice(0, 8);
  const activeAlerts = recent.filter((a) => !a.acknowledged);

  _dropdown.innerHTML = `
    <div class="notifications__header">
      <span class="notifications__title">Notificaciones</span>
      <span class="badge badge--warning">${activeAlerts.length} nuevas</span>
    </div>
    <div class="notifications__list">
      ${recent.length === 0
        ? '<div class="notifications__empty">Sin notificaciones</div>'
        : recent.map((a) => {
            const meta = SEVERITY_META[a.severity] || SEVERITY_META.low;
            return `
              <div class="notifications__item ${a.acknowledged ? "notifications__item--read" : ""}">
                <span class="notifications__icon">${meta.icon}</span>
                <div class="notifications__content">
                  <span class="notifications__text">${a.title}</span>
                  <span class="notifications__meta">${a.zone} · ${timeAgo(a.time)}</span>
                </div>
              </div>
            `;
          }).join("")
      }
    </div>
    <div class="notifications__footer">
      <button class="notifications__view-all" data-page="alerts">Ver todas las alertas</button>
    </div>
  `;

  /* Navigate to alerts page on "Ver todas" */
  const viewAllBtn = _dropdown.querySelector(".notifications__view-all");
  if (viewAllBtn) {
    viewAllBtn.addEventListener("click", () => {
      location.hash = "alerts";
      _closeDropdown();
    });
  }
}
