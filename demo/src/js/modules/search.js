/**
 * EchoSmart Demo — Search Module
 *
 * Provides real-time search/filter over the application pages.
 * Typing in the topbar search input filters the navigation and shows
 * a results dropdown with matching pages.
 *
 * @module modules/search
 */

/** Whether search event listeners have been bound */
let _bound = false;

/** @type {HTMLElement|null} */
let _resultsEl = null;

/**
 * Page search index — each entry maps a keyword set to a page route.
 * @type {Array<{page: string, label: string, keywords: string}>}
 */
const SEARCH_INDEX = [
  { page: "dashboard",  label: "Dashboard",     keywords: "dashboard panel inicio resumen temperatura humedad co2 luminosidad suelo gateways" },
  { page: "sensors",    label: "Sensores",      keywords: "sensores sensor ds18b20 dht22 bh1750 mhz19c soil ads1115 zona lectura" },
  { page: "alerts",     label: "Alertas",       keywords: "alertas alerta crítica alta media baja severidad notificación" },
  { page: "map",        label: "Mapa",          keywords: "mapa invernadero greenhouse camas pasillos heatmap calor sensor nodo" },
  { page: "reports",    label: "Reportes",       keywords: "reportes reporte análisis ia pdf exportar gráfico estadísticas" },
  { page: "settings",   label: "Configuración", keywords: "configuración ajustes umbral notificaciones gateway firmware idioma tema" },
  { page: "users",      label: "Usuarios",      keywords: "usuarios usuario admin operador visor roles email" },
  { page: "activity",   label: "Actividad",     keywords: "actividad registro log eventos historial sistema acciones" },
];

/**
 * Initialise search functionality.
 * Idempotent — safe to call multiple times.
 */
export function initSearch() {
  if (_bound) return;
  _bound = true;

  const searchInput = document.querySelector(".topbar__search input");
  const searchWrapper = document.querySelector(".topbar__search");
  if (!searchInput || !searchWrapper) return;

  _createResultsElement(searchWrapper);

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    if (query.length === 0) {
      _hideResults();
      return;
    }
    _search(query);
  });

  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      searchInput.value = "";
      _hideResults();
      searchInput.blur();
    }
  });

  document.addEventListener("click", (e) => {
    if (!searchWrapper.contains(e.target)) {
      _hideResults();
    }
  });
}

/* ===== Private helpers ===== */

function _createResultsElement(wrapper) {
  _resultsEl = document.createElement("div");
  _resultsEl.className = "search-results";
  _resultsEl.id = "searchResults";
  wrapper.style.position = "relative";
  wrapper.appendChild(_resultsEl);

  /* Event delegation — single listener handles all result clicks */
  _resultsEl.addEventListener("click", (e) => {
    const item = e.target.closest(".search-results__item");
    if (!item) return;
    location.hash = item.dataset.page;
    _hideResults();
    const searchInput = document.querySelector(".topbar__search input");
    if (searchInput) searchInput.value = "";
  });
}

function _search(query) {
  const terms = query.split(/\s+/);
  const matches = SEARCH_INDEX.filter((entry) =>
    terms.every((term) => entry.keywords.includes(term) || entry.label.toLowerCase().includes(term))
  );

  if (matches.length === 0) {
    _resultsEl.innerHTML = `<div class="search-results__empty">Sin resultados para "${query}"</div>`;
  } else {
    _resultsEl.innerHTML = matches.map((m) => `
      <button class="search-results__item" data-page="${m.page}">
        <span class="search-results__label">${m.label}</span>
        <span class="search-results__hint">Ir a la página</span>
      </button>
    `).join("");
  }

  _resultsEl.classList.add("search-results--open");
}

function _hideResults() {
  if (_resultsEl) {
    _resultsEl.classList.remove("search-results--open");
  }
}
