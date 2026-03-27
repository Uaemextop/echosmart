/**
 * EchoSmart Demo — Router
 *
 * Simple hash-based SPA router that shows/hides page sections.
 */

/**
 * Initialise routing.
 * @param {Record<string, () => void>} pageRenderers  – key = page id, value = render function
 * @param {string} defaultPage
 */
export function initRouter(pageRenderers, defaultPage) {
  function navigate() {
    const hash = location.hash.replace("#", "") || defaultPage;
    const pageName = pageRenderers[hash] ? hash : defaultPage;

    /* Hide all pages */
    document.querySelectorAll(".page").forEach((el) => {
      el.classList.add("page--hidden");
    });

    /* Show active */
    const target = document.getElementById("page-" + pageName);
    if (target) target.classList.remove("page--hidden");

    /* Update sidebar active state */
    document.querySelectorAll(".sidebar__link").forEach((link) => {
      link.classList.toggle("active", link.dataset.page === pageName);
    });

    /* Update topbar title */
    const titles = {
      dashboard: "Dashboard",
      sensors: "Sensores",
      alerts: "Alertas",
      map: "Mapa",
      reports: "Reportes",
      settings: "Configuración",
      users: "Usuarios",
      activity: "Actividad",
    };
    const topTitle = document.getElementById("topbarTitle");
    if (topTitle) topTitle.textContent = titles[pageName] || pageName;

    /* Call page renderer */
    if (pageRenderers[pageName]) pageRenderers[pageName]();
  }

  /* Sidebar link clicks */
  document.querySelectorAll(".sidebar__link[data-page]").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      location.hash = link.dataset.page;
    });
  });

  window.addEventListener("hashchange", navigate);
  navigate();
}
