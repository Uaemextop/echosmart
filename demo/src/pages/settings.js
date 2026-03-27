/**
 * EchoSmart Demo — Settings Page Renderer
 *
 * Manages toggle switches with idempotent event binding
 * to prevent duplicate listeners on repeated navigation.
 */

/** Track whether toggle listeners have been bound */
let togglesBound = false;

export function renderSettings() {
  if (togglesBound) return;
  togglesBound = true;

  document.querySelectorAll(".toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.classList.toggle("active");
    });
  });
}
