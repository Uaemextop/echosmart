/**
 * EchoSmart Demo — PDF Export Module
 *
 * Exports the AI report to PDF using the browser's print dialog.
 * Opens a new window with print-optimized styles and triggers print.
 *
 * @module pdf-export
 */

/** CSS stylesheet optimized for print/PDF output (white background) */
const PRINT_STYLES = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #fff; color: #222; padding: 20px; font-size: 12px; }
  .ai-report { max-width: 800px; margin: 0 auto; }
  .ai-report__brand-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 2px solid #00E676; margin-bottom: 20px; }
  .ai-report__brand-logo { display: flex; align-items: center; gap: 12px; }
  .ai-report__brand-name { font-size: 20px; font-weight: 700; color: #2E7D32; }
  .ai-report__brand-subtitle { font-size: 11px; color: #666; }
  .ai-report__brand-date { text-align: right; font-size: 11px; color: #666; }
  .ai-report__model-info { background: #f5f5f5; padding: 8px 14px; border-radius: 6px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; font-size: 11px; }
  .ai-report__model-badge { background: #e8f5e9; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 10px; }
  .ai-report__section { margin-bottom: 24px; }
  .ai-report__section-title { font-size: 14px; font-weight: 700; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #eee; }
  .ai-report__summary-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
  .ai-report__summary-item { padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; text-align: center; }
  .ai-report__summary-label { display: block; font-size: 10px; color: #666; text-transform: uppercase; }
  .ai-report__summary-value { display: block; font-size: 18px; font-weight: 700; margin: 4px 0; }
  .ai-report__summary-range { display: block; font-size: 9px; color: #999; }
  .ai-report__instruction-note { background: #fff3e0; padding: 10px; border-radius: 6px; font-size: 10px; color: #e65100; margin-bottom: 12px; border-left: 3px solid #ff9100; }
  .ai-report__alert-card { padding: 12px; margin-bottom: 10px; border: 1px solid #e0e0e0; border-radius: 6px; }
  .ai-report__alert-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .ai-report__alert-name { font-weight: 700; font-size: 13px; }
  .ai-report__alert-risk { padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
  .ai-report__alert-reason { font-size: 11px; color: #444; margin-bottom: 6px; }
  .ai-report__alert-action { font-size: 11px; color: #2E7D32; background: #e8f5e9; padding: 6px 10px; border-radius: 4px; }
  .ai-report__diagram { margin: 12px 0; }
  .ai-report__diagram-svg { width: 100%; max-height: 250px; }
  .ai-report__diagram-svg text { fill: #333; }
  .ai-report__diagram-svg rect { stroke-opacity: 0.5; }
  .ai-report__diagram-svg path { stroke: #ccc; }
  .ai-report__diagram-svg line { stroke: #ccc; }
  .ai-report__table { width: 100%; border-collapse: collapse; font-size: 11px; }
  .ai-report__table th { text-align: left; padding: 8px; border-bottom: 2px solid #e0e0e0; font-size: 10px; text-transform: uppercase; color: #666; }
  .ai-report__table td { padding: 8px; border-bottom: 1px solid #f0f0f0; }
  .ai-report__scale-bar { position: relative; height: 8px; background: #eee; border-radius: 4px; min-width: 100px; }
  .ai-report__scale-optimal { position: absolute; top: 0; height: 100%; background: rgba(0,200,83,0.2); border-radius: 4px; }
  .ai-report__scale-marker { position: absolute; top: -2px; width: 4px; height: 12px; border-radius: 2px; transform: translateX(-2px); }
  .ai-report__recommendations { display: grid; gap: 10px; }
  .ai-report__rec-item { display: flex; gap: 12px; padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; }
  .ai-report__rec-number { width: 28px; height: 28px; border-radius: 50%; background: #e8f5e9; color: #2E7D32; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; }
  .ai-report__rec-title { font-weight: 700; font-size: 12px; margin-bottom: 4px; }
  .ai-report__rec-text { font-size: 11px; color: #555; line-height: 1.5; }
  .ai-report__footer { margin-top: 30px; padding-top: 16px; border-top: 2px solid #00E676; text-align: center; }
  .ai-report__footer-brand { display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 6px; font-weight: 600; color: #2E7D32; }
  .ai-report__footer-meta { font-size: 9px; color: #999; margin-bottom: 6px; }
  .ai-report__footer-disclaimer { font-size: 9px; color: #999; font-style: italic; }
  @media print {
    body { padding: 0; }
    .ai-report__alert-card { break-inside: avoid; }
    .ai-report__section { break-inside: avoid; }
  }
`;

/**
 * Export the AI report section to PDF via print dialog.
 * Opens a new window with the report content and print-optimized styles.
 *
 * Handles popup blocker scenarios with a user-friendly alert.
 */
export function exportPDF() {
  const printArea = document.getElementById("aiReportPrintable");
  if (!printArea) return;

  const printWindow = window.open("", "_blank");

  if (!printWindow) {
    window.alert("No se pudo abrir la ventana de impresión. Por favor, permite las ventanas emergentes para este sitio e inténtalo de nuevo.");
    return;
  }

  const htmlContent = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <title>EchoSmart — Reporte IA</title>
  <style>${PRINT_STYLES}</style>
</head>
<body>
  ${printArea.innerHTML}
</body>
</html>`;

  printWindow.document.write(htmlContent);
  printWindow.document.close();

  /* Wait for DOM to fully load before triggering print */
  printWindow.onload = () => {
    printWindow.print();
  };
}
