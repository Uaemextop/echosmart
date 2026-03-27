/**
 * EchoSmart Demo — Map Page Renderer
 */

import { ICONS } from "../js/modules/icons.js";

const PINS = [
  { id: "gw1", label: "Gateway-01 · Zona A", x: "25%", y: "35%", status: "online" },
  { id: "gw2", label: "Gateway-02 · Zona B", x: "55%", y: "55%", status: "online" },
  { id: "gw3", label: "Gateway-03 · Zona C", x: "75%", y: "30%", status: "warning" },
];

let rendered = false;

export function renderMap() {
  if (rendered) return;
  rendered = true;

  const container = document.getElementById("mapPins");
  if (!container) return;

  container.innerHTML = PINS.map((p) => `
    <div class="map-pin" style="left:${p.x}; top:${p.y};">
      <svg viewBox="0 0 24 24" fill="none"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" fill="${p.status === "online" ? "#00E676" : "#FF9100"}" opacity="0.8"/><circle cx="12" cy="10" r="3" fill="#fff"/></svg>
      <span class="map-pin__label">${p.label}</span>
    </div>
  `).join("");
}
