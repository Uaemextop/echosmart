/**
 * EchoSmart Demo — Settings Page Renderer
 */

export function renderSettings() {
  /* Toggle switches */
  document.querySelectorAll(".toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.classList.toggle("active");
    });
  });
}
