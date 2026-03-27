/**
 * EchoSmart Demo — Alerts Page Renderer
 */

import { timeAgo, activeCount } from "../js/modules/alerts.js";

export function renderAlerts(alerts) {
  const tbody = document.getElementById("alertsTableBody");
  if (!tbody) return;

  tbody.innerHTML = alerts.map((a) => `
    <tr>
      <td>
        <div class="alerts-table__severity">
          <span class="alerts-table__dot alerts-table__dot--${a.severity}"></span>
          <span>${capitalize(a.severity)}</span>
        </div>
      </td>
      <td>${a.title}</td>
      <td>${a.zone}</td>
      <td>${a.sensor}</td>
      <td>${timeAgo(a.time)}</td>
      <td>${a.acknowledged ? '<span class="badge badge--info">Cerrada</span>' : '<span class="badge badge--warning">Activa</span>'}</td>
    </tr>
  `).join("");

  const countEl = document.getElementById("alertsCount");
  if (countEl) countEl.textContent = activeCount(alerts) + " activas";
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
