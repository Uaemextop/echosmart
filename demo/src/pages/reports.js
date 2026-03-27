/**
 * EchoSmart Demo — Reports Page Renderer
 *
 * Enhanced with gauge charts, bar charts, statistics summary,
 * AI-powered analysis, and PDF export.
 */

import { Chart } from "chart.js";
import { createLineChart, make24hLabels } from "../js/modules/charts.js";
import { getColors, getSpecs, formatValue, computeStats, checkStatus } from "../js/modules/sensors.js";
import { LOGO_ICON } from "../js/modules/icons.js";

let chartsCreated = false;

/* ---- Gauge drawing helper ---- */
function drawGauge(canvasId, value, min, max, optMin, optMax, color, unit) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width = canvas.parentElement.offsetWidth || 160;
  const h = canvas.height = 110;
  const cx = w / 2, cy = h - 10, r = Math.min(w / 2 - 10, 80);

  ctx.clearRect(0, 0, w, h);

  /* Background arc */
  ctx.beginPath();
  ctx.arc(cx, cy, r, Math.PI, 0, false);
  ctx.lineWidth = 12;
  ctx.strokeStyle = "rgba(255,255,255,0.06)";
  ctx.stroke();

  /* Optimal range arc */
  const optStart = Math.PI + ((optMin - min) / (max - min)) * Math.PI;
  const optEnd = Math.PI + ((optMax - min) / (max - min)) * Math.PI;
  ctx.beginPath();
  ctx.arc(cx, cy, r, optStart, optEnd, false);
  ctx.lineWidth = 12;
  ctx.strokeStyle = "rgba(0,230,118,0.2)";
  ctx.stroke();

  /* Value arc */
  const valueAngle = Math.PI + (Math.max(0, Math.min(1, (value - min) / (max - min)))) * Math.PI;
  ctx.beginPath();
  ctx.arc(cx, cy, r, Math.PI, valueAngle, false);
  ctx.lineWidth = 12;
  ctx.lineCap = "round";
  ctx.strokeStyle = color;
  ctx.stroke();

  /* Value text */
  ctx.fillStyle = "#E0E0E0";
  ctx.font = "bold 18px -apple-system, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(value.toFixed(1) + unit, cx, cy - 20);

  /* Min/Max labels */
  ctx.fillStyle = "#546e7a";
  ctx.font = "10px -apple-system, sans-serif";
  ctx.textAlign = "left";
  ctx.fillText(min + unit, cx - r - 5, cy + 14);
  ctx.textAlign = "right";
  ctx.fillText(max + unit, cx + r + 5, cy + 14);

  /* Optimal label */
  ctx.fillStyle = "#00E676";
  ctx.font = "9px -apple-system, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(`Óptimo: ${optMin}–${optMax}`, cx, cy + 2);
}

/* ---- Bar chart for comparing sensors ---- */
function createBarChart(canvasId, sensors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const COLORS = getColors();
  const SPECS = getSpecs();

  const keys = ["temperature", "humidity", "co2", "light", "soil"];
  const labels = ["Temp", "Humedad", "CO₂", "Luz", "Suelo"];
  const normalizedValues = keys.map(k => {
    const spec = SPECS[k];
    return ((sensors[k].value - spec.min) / (spec.max - spec.min)) * 100;
  });
  const bgColors = keys.map(k => COLORS[k] + "40");
  const borderColors = keys.map(k => COLORS[k]);

  return new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Nivel actual (%)",
        data: normalizedValues,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 1.5,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111111",
          titleColor: "#E0E0E0",
          bodyColor: "#E0E0E0",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          cornerRadius: 8,
          callbacks: {
            label: (ctx) => `${ctx.parsed.y.toFixed(1)}% del rango`,
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: {
          min: 0, max: 100,
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { font: { size: 11 }, callback: (v) => v + "%" },
        },
      },
    },
  });
}

/* ---- AI report generation (simulated with GitHub Models prompt pattern) ---- */
function generateAIReport(sensors) {
  const SPECS = getSpecs();
  const COLORS = getColors();
  const now = new Date();
  const dateStr = now.toLocaleDateString("es-MX", { year: "numeric", month: "long", day: "numeric" });
  const timeStr = now.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });

  const tempStats = computeStats(sensors.temperature.history);
  const humStats = computeStats(sensors.humidity.history);
  const co2Stats = computeStats(sensors.co2.history);
  const lightStats = computeStats(sensors.light.history);
  const soilStats = computeStats(sensors.soil.history);

  const tempStatus = checkStatus("temperature", sensors.temperature.value);
  const humStatus = checkStatus("humidity", sensors.humidity.value);
  const co2Status = checkStatus("co2", sensors.co2.value);

  /* Disease risk analysis based on conditions */
  const diseases = [];

  if (sensors.humidity.value > 85 && sensors.temperature.value > 25) {
    diseases.push({
      name: "Botrytis cinerea (Moho gris)",
      risk: "ALTO",
      color: "#FF1744",
      reason: `Humedad ${sensors.humidity.value.toFixed(0)}% > 85% combinada con temperatura ${sensors.temperature.value.toFixed(1)}°C > 25°C crea condiciones ideales para proliferación de esporas.`,
      action: "Reducir humedad inmediatamente. Aumentar ventilación. Aplicar fungicida preventivo a base de iprodiona.",
    });
  } else if (sensors.humidity.value > 75) {
    diseases.push({
      name: "Botrytis cinerea (Moho gris)",
      risk: "MEDIO",
      color: "#FF9100",
      reason: `Humedad ${sensors.humidity.value.toFixed(0)}% cercana al umbral crítico de 85%. La combinación con temperatura actual de ${sensors.temperature.value.toFixed(1)}°C puede favorecer condiciones de propagación.`,
      action: "Monitorear continuamente. Mejorar la circulación de aire entre plantas. Considerar deshumidificación preventiva.",
    });
  }

  if (sensors.temperature.value > 30) {
    diseases.push({
      name: "Estrés térmico / Marchitamiento",
      risk: "ALTO",
      color: "#FF1744",
      reason: `Temperatura ${sensors.temperature.value.toFixed(1)}°C excede significativamente el rango óptimo de 18–28°C. Las plantas sufren daño celular y reducción en la fotosíntesis.`,
      action: "Activar sistema de enfriamiento. Aumentar riego por aspersión. Usar mallas de sombreo al 50%.",
    });
  } else if (sensors.temperature.value > 28) {
    diseases.push({
      name: "Estrés térmico leve",
      risk: "MEDIO",
      color: "#FF9100",
      reason: `Temperatura ${sensors.temperature.value.toFixed(1)}°C en el límite superior del rango óptimo. Prolongar esta condición puede reducir el rendimiento de los cultivos.`,
      action: "Verificar sistema de ventilación. Preparar enfriamiento adicional si la tendencia continúa.",
    });
  }

  if (sensors.temperature.value < 15) {
    diseases.push({
      name: "Daño por frío / Helada",
      risk: "ALTO",
      color: "#FF1744",
      reason: `Temperatura ${sensors.temperature.value.toFixed(1)}°C muy por debajo del rango óptimo. Riesgo de daño celular por cristalización del agua intracelular.`,
      action: "Activar calefacción de emergencia. Cerrar ventilaciones. Cubrir cultivos sensibles con manta térmica.",
    });
  }

  if (sensors.humidity.value > 80 && sensors.temperature.value > 20 && sensors.temperature.value < 28) {
    diseases.push({
      name: "Mildiu (Peronospora spp.)",
      risk: "MEDIO",
      color: "#FF9100",
      reason: `Humedad relativa ${sensors.humidity.value.toFixed(0)}% > 80% con temperatura entre 20–28°C (actual: ${sensors.temperature.value.toFixed(1)}°C). Estas condiciones permiten la germinación de esporas de mildiu.`,
      action: "Aplicar fungicida preventivo a base de metalaxil. Reducir densidad de follaje. Mejorar drenaje.",
    });
  }

  if (sensors.co2.value > 1000) {
    diseases.push({
      name: "Exceso de CO₂ — Toxicidad",
      risk: "MEDIO",
      color: "#FF9100",
      reason: `Nivel de CO₂ ${sensors.co2.value.toFixed(0)} ppm supera el umbral de 1000 ppm. Concentraciones elevadas pueden causar cierre estomático y reducción en la transpiración.`,
      action: "Incrementar ventilación natural o forzada. Verificar fuentes de combustión. Revisar generadores de CO₂.",
    });
  }

  if (sensors.soil.value < 40) {
    diseases.push({
      name: "Déficit hídrico / Estrés por sequía",
      risk: "ALTO",
      color: "#FF1744",
      reason: `Humedad del suelo ${sensors.soil.value.toFixed(0)}% por debajo del mínimo óptimo de 50%. Las raíces no pueden absorber nutrientes adecuadamente.`,
      action: "Activar riego de emergencia. Verificar sistema de irrigación por goteo. Aplicar mulch para retención de humedad.",
    });
  } else if (sensors.soil.value < 50) {
    diseases.push({
      name: "Humedad de suelo baja",
      risk: "MEDIO",
      color: "#FF9100",
      reason: `Humedad del suelo ${sensors.soil.value.toFixed(0)}% se acerca al límite inferior óptimo de 50%. Las plantas pueden mostrar signos de estrés hídrico leve.`,
      action: "Programar riego adicional. Monitorear curva de evapotranspiración.",
    });
  }

  if (sensors.light.value < 5000) {
    diseases.push({
      name: "Deficiencia lumínica",
      risk: "MEDIO",
      color: "#FF9100",
      reason: `Luminosidad ${sensors.light.value.toFixed(0)} lux por debajo del mínimo óptimo de 10,000 lux. Insuficiente para fotosíntesis eficiente en la mayoría de cultivos de invernadero.`,
      action: "Activar iluminación suplementaria LED. Limpiar cubiertas de invernadero. Verificar horario de luz.",
    });
  }

  /* If everything is optimal, add a positive message */
  if (diseases.length === 0) {
    diseases.push({
      name: "Sin riesgos detectados",
      risk: "BAJO",
      color: "#00E676",
      reason: "Todas las condiciones ambientales están dentro de los rangos óptimos para el cultivo en invernadero.",
      action: "Continuar con el monitoreo regular. Mantener las prácticas actuales de manejo ambiental.",
    });
  }

  return { dateStr, timeStr, tempStats, humStats, co2Stats, lightStats, soilStats, diseases, tempStatus, humStatus, co2Status };
}

export function renderReports(sensors) {
  const COLORS = getColors();
  const SPECS = getSpecs();

  /* ===== Section 1: Statistics summary cards ===== */
  const summaryEl = document.getElementById("reportsSummary");
  if (summaryEl) {
    const sensorKeys = [
      { key: "temperature", label: "Temperatura", icon: "🌡️" },
      { key: "humidity", label: "Humedad", icon: "💧" },
      { key: "co2", label: "CO₂", icon: "☁️" },
      { key: "light", label: "Luminosidad", icon: "☀️" },
      { key: "soil", label: "Suelo", icon: "🌱" },
    ];
    summaryEl.innerHTML = sensorKeys.map(s => {
      const stats = computeStats(sensors[s.key].history);
      const status = checkStatus(s.key, sensors[s.key].value);
      const statusClass = status === "optimal" ? "success" : status === "warning" ? "warning" : "danger";
      return `
        <div class="report-summary-card">
          <div class="report-summary-card__header">
            <span class="report-summary-card__icon">${s.icon}</span>
            <span class="report-summary-card__label">${s.label}</span>
            <span class="badge badge--${statusClass}">${status === "optimal" ? "Normal" : status === "warning" ? "Alerta" : "Crítico"}</span>
          </div>
          <div class="report-summary-card__value" style="color:${COLORS[s.key]}">${formatValue(s.key, sensors[s.key].value)}</div>
          <div class="report-summary-card__stats">
            <span>Mín: ${formatValue(s.key, stats.min)}</span>
            <span>Máx: ${formatValue(s.key, stats.max)}</span>
            <span>Prom: ${formatValue(s.key, stats.avg)}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  /* ===== Section 2: Gauge charts ===== */
  const gauges = [
    { id: "gaugeTemp", key: "temperature", unit: "°C" },
    { id: "gaugeHum", key: "humidity", unit: "%" },
    { id: "gaugeCo2", key: "co2", unit: "ppm" },
    { id: "gaugeSoil", key: "soil", unit: "%" },
  ];
  gauges.forEach(g => {
    const spec = SPECS[g.key];
    drawGauge(g.id, sensors[g.key].value, spec.min, spec.max, spec.optMin, spec.optMax, COLORS[g.key], g.unit);
  });

  /* ===== Section 3: Line charts (create only once) ===== */
  if (!chartsCreated) {
    chartsCreated = true;

    const lineConfigs = [
      { id: "reportTempChart", label: "Temperatura (°C)", key: "temperature", yMin: 10, yMax: 40 },
      { id: "reportHumChart", label: "Humedad (%)", key: "humidity", yMin: 20, yMax: 100 },
      { id: "reportCo2Chart", label: "CO₂ (ppm)", key: "co2", yMin: 300, yMax: 1500 },
      { id: "reportLightChart", label: "Luminosidad (lux)", key: "light", yMin: 0, yMax: 50000 },
    ];

    for (const cfg of lineConfigs) {
      const canvas = document.getElementById(cfg.id);
      if (canvas && sensors[cfg.key]) {
        createLineChart(canvas, cfg.label, sensors[cfg.key].history, COLORS[cfg.key], cfg.yMin, cfg.yMax);
      }
    }

    /* Bar chart */
    createBarChart("reportBarChart", sensors);
  }

  /* ===== Section 4: AI Analysis Report ===== */
  const aiContainer = document.getElementById("aiReportContent");
  if (aiContainer) {
    const report = generateAIReport(sensors);
    aiContainer.innerHTML = renderAIReportHTML(sensors, report);
  }

  /* ===== PDF Export button ===== */
  const pdfBtn = document.getElementById("exportPdfBtn");
  if (pdfBtn && !pdfBtn.dataset.bound) {
    pdfBtn.dataset.bound = "true";
    pdfBtn.addEventListener("click", () => exportPDF());
  }
}

function renderAIReportHTML(sensors, report) {
  const COLORS = getColors();
  const highRisks = report.diseases.filter(d => d.risk === "ALTO");
  const medRisks = report.diseases.filter(d => d.risk === "MEDIO");
  const lowRisks = report.diseases.filter(d => d.risk === "BAJO");

  return `
    <!-- AI Report Header with Branding -->
    <div class="ai-report" id="aiReportPrintable">
      <div class="ai-report__brand-header">
        <div class="ai-report__brand-logo">
          <svg viewBox="0 0 120 120" fill="none" width="40" height="40">
            <defs>
              <linearGradient id="rlg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00E676"/><stop offset="100%" stop-color="#2E7D32"/>
              </linearGradient>
              <linearGradient id="rsg" x1="0%" y1="50%" x2="100%" y2="50%">
                <stop offset="0%" stop-color="#00BCD4"/><stop offset="100%" stop-color="#00838F"/>
              </linearGradient>
            </defs>
            <path d="M30 95Q18 55 45 28Q58 15 78 15Q88 15 95 20Q95 35 88 52Q72 85 35 95Q32 95 30 95z" fill="url(#rlg)" opacity="0.9"/>
            <path d="M72 28a20 20 0 0 1 14 14" stroke="url(#rsg)" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.9"/>
            <path d="M78 18a30 30 0 0 1 22 22" stroke="url(#rsg)" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.6"/>
          </svg>
          <div>
            <div class="ai-report__brand-name">EchoSmart</div>
            <div class="ai-report__brand-subtitle">Invernadero Inteligente — Reporte de Análisis IA</div>
          </div>
        </div>
        <div class="ai-report__brand-date">
          <div>${report.dateStr}</div>
          <div class="text-muted">${report.timeStr} hrs</div>
        </div>
      </div>

      <!-- AI Model Info -->
      <div class="ai-report__model-info">
        <span class="ai-report__model-badge">🤖 GitHub Models · GPT-4o</span>
        <span class="ai-report__model-text">Análisis generado con inteligencia artificial basado en datos de sensores en tiempo real</span>
      </div>

      <!-- Executive Summary -->
      <div class="ai-report__section">
        <h3 class="ai-report__section-title">📊 Resumen Ejecutivo</h3>
        <div class="ai-report__summary-grid">
          <div class="ai-report__summary-item">
            <span class="ai-report__summary-label">Temperatura</span>
            <span class="ai-report__summary-value" style="color:${COLORS.temperature}">${sensors.temperature.value.toFixed(1)}°C</span>
            <span class="ai-report__summary-range">Rango 24h: ${report.tempStats.min}–${report.tempStats.max}°C</span>
          </div>
          <div class="ai-report__summary-item">
            <span class="ai-report__summary-label">Humedad</span>
            <span class="ai-report__summary-value" style="color:${COLORS.humidity}">${sensors.humidity.value.toFixed(0)}%</span>
            <span class="ai-report__summary-range">Rango 24h: ${report.humStats.min}–${report.humStats.max}%</span>
          </div>
          <div class="ai-report__summary-item">
            <span class="ai-report__summary-label">CO₂</span>
            <span class="ai-report__summary-value" style="color:${COLORS.co2}">${sensors.co2.value.toFixed(0)} ppm</span>
            <span class="ai-report__summary-range">Rango 24h: ${report.co2Stats.min}–${report.co2Stats.max} ppm</span>
          </div>
          <div class="ai-report__summary-item">
            <span class="ai-report__summary-label">Luminosidad</span>
            <span class="ai-report__summary-value" style="color:${COLORS.light}">${sensors.light.value.toFixed(0)} lux</span>
            <span class="ai-report__summary-range">Rango 24h: ${report.lightStats.min}–${report.lightStats.max} lux</span>
          </div>
          <div class="ai-report__summary-item">
            <span class="ai-report__summary-label">Suelo</span>
            <span class="ai-report__summary-value" style="color:${COLORS.soil}">${sensors.soil.value.toFixed(0)}%</span>
            <span class="ai-report__summary-range">Rango 24h: ${report.soilStats.min}–${report.soilStats.max}%</span>
          </div>
        </div>
      </div>

      <!-- Disease Risk Alerts -->
      <div class="ai-report__section">
        <h3 class="ai-report__section-title">⚠️ Alertas de Enfermedades y Riesgos</h3>
        <p class="ai-report__instruction-note">
          <strong>Instrucciones al modelo IA:</strong> Analizar condiciones ambientales del invernadero.
          Identificar riesgos fitosanitarios basados en combinaciones de temperatura, humedad relativa,
          CO₂, luminosidad y humedad del suelo. Correlacionar con patógenos comunes en cultivos de invernadero.
          Priorizar alertas por nivel de riesgo y proporcionar acciones correctivas específicas.
        </p>
        ${report.diseases.map(d => `
          <div class="ai-report__alert-card" style="border-left: 3px solid ${d.color}">
            <div class="ai-report__alert-header">
              <span class="ai-report__alert-name">${d.name}</span>
              <span class="ai-report__alert-risk" style="background: ${d.color}20; color: ${d.color}">${d.risk}</span>
            </div>
            <div class="ai-report__alert-reason">
              <strong>Análisis:</strong> ${d.reason}
            </div>
            <div class="ai-report__alert-action">
              <strong>Acción recomendada:</strong> ${d.action}
            </div>
          </div>
        `).join("")}
      </div>

      <!-- Environmental Conditions Diagram -->
      <div class="ai-report__section">
        <h3 class="ai-report__section-title">🏗️ Diagrama de Condiciones Ambientales</h3>
        <div class="ai-report__diagram">
          <svg viewBox="0 0 600 280" class="ai-report__diagram-svg">
            <!-- Greenhouse outline -->
            <path d="M50 220 L50 100 L300 30 L550 100 L550 220 Z" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2"/>
            <path d="M50 100 L300 30 L550 100" fill="rgba(0,230,118,0.05)" stroke="rgba(0,230,118,0.3)" stroke-width="1.5"/>
            <line x1="50" y1="220" x2="550" y2="220" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>

            <!-- Zone A -->
            <rect x="70" y="110" width="150" height="100" rx="4" fill="${COLORS.temperature}15" stroke="${COLORS.temperature}40" stroke-width="1"/>
            <text x="145" y="135" text-anchor="middle" fill="${COLORS.temperature}" font-size="12" font-weight="600">Zona A</text>
            <text x="145" y="155" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="700">${sensors.temperature.value.toFixed(1)}°C</text>
            <text x="145" y="175" text-anchor="middle" fill="${COLORS.humidity}" font-size="11">${sensors.humidity.value.toFixed(0)}% HR</text>
            <text x="145" y="195" text-anchor="middle" fill="${COLORS.co2}" font-size="10">${sensors.co2.value.toFixed(0)} ppm CO₂</text>

            <!-- Zone B -->
            <rect x="230" y="110" width="140" height="100" rx="4" fill="${COLORS.light}15" stroke="${COLORS.light}40" stroke-width="1"/>
            <text x="300" y="135" text-anchor="middle" fill="${COLORS.light}" font-size="12" font-weight="600">Zona B</text>
            <text x="300" y="155" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="700">${sensors.light.value.toFixed(0)} lux</text>
            <text x="300" y="175" text-anchor="middle" fill="${COLORS.soil}" font-size="11">${sensors.soil.value.toFixed(0)}% Suelo</text>
            <text x="300" y="195" text-anchor="middle" fill="${COLORS.co2}" font-size="10">${sensors.co2.value.toFixed(0)} ppm CO₂</text>

            <!-- Zone C -->
            <rect x="380" y="110" width="150" height="100" rx="4" fill="${COLORS.humidity}15" stroke="${COLORS.humidity}40" stroke-width="1"/>
            <text x="455" y="135" text-anchor="middle" fill="${COLORS.humidity}" font-size="12" font-weight="600">Zona C</text>
            <text x="455" y="155" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="700">${(sensors.temperature.value - 1.2).toFixed(1)}°C</text>
            <text x="455" y="175" text-anchor="middle" fill="${COLORS.humidity}" font-size="11">${sensors.humidity.value.toFixed(0)}% HR</text>

            <!-- Sensors icons -->
            <circle cx="110" cy="150" r="5" fill="${COLORS.temperature}"/>
            <circle cx="180" cy="170" r="5" fill="${COLORS.humidity}"/>
            <circle cx="280" cy="160" r="5" fill="${COLORS.light}"/>
            <circle cx="320" cy="180" r="5" fill="${COLORS.soil}"/>
            <circle cx="430" cy="150" r="5" fill="${COLORS.temperature}"/>
            <circle cx="480" cy="170" r="5" fill="${COLORS.humidity}"/>

            <!-- Title -->
            <text x="300" y="260" text-anchor="middle" fill="#546e7a" font-size="11">Distribución de sensores — Invernadero Principal</text>
          </svg>
        </div>
      </div>

      <!-- Optimal Ranges Schema -->
      <div class="ai-report__section">
        <h3 class="ai-report__section-title">📐 Esquema de Rangos Óptimos</h3>
        <div class="ai-report__ranges-table">
          <table class="ai-report__table">
            <thead>
              <tr>
                <th>Parámetro</th>
                <th>Valor Actual</th>
                <th>Rango Óptimo</th>
                <th>Rango Sensor</th>
                <th>Estado</th>
                <th>Escala Visual</th>
              </tr>
            </thead>
            <tbody>
              ${[
                { key: "temperature", label: "Temperatura", icon: "🌡️" },
                { key: "humidity", label: "Humedad", icon: "💧" },
                { key: "co2", label: "CO₂", icon: "☁️" },
                { key: "light", label: "Luminosidad", icon: "☀️" },
                { key: "soil", label: "Suelo", icon: "🌱" },
              ].map(s => {
                const spec = getSpecs()[s.key];
                const val = sensors[s.key].value;
                const status = checkStatus(s.key, val);
                const statusLabel = status === "optimal" ? "✅ Normal" : status === "warning" ? "⚠️ Alerta" : "🔴 Crítico";
                const pct = ((val - spec.min) / (spec.max - spec.min)) * 100;
                const optStartPct = ((spec.optMin - spec.min) / (spec.max - spec.min)) * 100;
                const optEndPct = ((spec.optMax - spec.min) / (spec.max - spec.min)) * 100;
                return `
                  <tr>
                    <td>${s.icon} ${s.label}</td>
                    <td style="color:${COLORS[s.key]};font-weight:600">${formatValue(s.key, val)}</td>
                    <td>${spec.optMin}–${spec.optMax}${spec.unit}</td>
                    <td>${spec.min}–${spec.max}${spec.unit}</td>
                    <td>${statusLabel}</td>
                    <td>
                      <div class="ai-report__scale-bar">
                        <div class="ai-report__scale-optimal" style="left:${optStartPct}%;width:${optEndPct - optStartPct}%"></div>
                        <div class="ai-report__scale-marker" style="left:${Math.min(100, Math.max(0, pct))}%;background:${COLORS[s.key]}"></div>
                      </div>
                    </td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Engineering Recommendations -->
      <div class="ai-report__section">
        <h3 class="ai-report__section-title">🔧 Recomendaciones para el Ingeniero</h3>
        <div class="ai-report__recommendations">
          <div class="ai-report__rec-item">
            <div class="ai-report__rec-number">1</div>
            <div>
              <div class="ai-report__rec-title">Calibración de Sensores</div>
              <div class="ai-report__rec-text">Verificar calibración del sensor DS18B20 cada 30 días. Desviación máxima aceptable: ±0.5°C. Comparar con termómetro de referencia certificado.</div>
            </div>
          </div>
          <div class="ai-report__rec-item">
            <div class="ai-report__rec-number">2</div>
            <div>
              <div class="ai-report__rec-title">Mantenimiento de Ventilación</div>
              <div class="ai-report__rec-text">Inspeccionar motores de ventilación y filtros. Limpiar filtros cada 15 días. Verificar apertura/cierre automatizado de ventanas cenitales y laterales.</div>
            </div>
          </div>
          <div class="ai-report__rec-item">
            <div class="ai-report__rec-number">3</div>
            <div>
              <div class="ai-report__rec-title">Sistema de Riego</div>
              <div class="ai-report__rec-text">Revisar goteros y electroválvulas. Verificar presión del sistema (1.5–2.5 bar). Monitorear uniformidad de distribución con coeficiente de Christiansen > 85%.</div>
            </div>
          </div>
          <div class="ai-report__rec-item">
            <div class="ai-report__rec-number">4</div>
            <div>
              <div class="ai-report__rec-title">Monitoreo de CO₂</div>
              <div class="ai-report__rec-text">Calibrar sensor MH-Z19C con gas de referencia (400 ppm). Verificar sellado del invernadero para eficiencia de inyección de CO₂. Evaluar costo-beneficio de enriquecimiento carbónico.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="ai-report__footer">
        <div class="ai-report__footer-brand">
          <svg viewBox="0 0 120 120" fill="none" width="20" height="20">
            <path d="M30 95Q18 55 45 28Q58 15 78 15Q88 15 95 20Q95 35 88 52Q72 85 35 95Q32 95 30 95z" fill="#00E676" opacity="0.9"/>
          </svg>
          <span>EchoSmart · Invernadero Inteligente</span>
        </div>
        <div class="ai-report__footer-meta">
          Reporte generado el ${report.dateStr} a las ${report.timeStr} · Análisis por GitHub Models (GPT-4o) · v1.0.0
        </div>
        <div class="ai-report__footer-disclaimer">
          Este reporte es generado por inteligencia artificial con fines informativos. Las recomendaciones deben ser evaluadas por un ingeniero agrónomo antes de su implementación.
        </div>
      </div>
    </div>
  `;
}

/* ---- PDF Export ---- */
function exportPDF() {
  const printArea = document.getElementById("aiReportPrintable");
  if (!printArea) return;

  const printWindow = window.open("", "_blank");
  if (!printWindow) return;

  printWindow.document.write(`<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <title>EchoSmart — Reporte IA</title>
  <style>
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
  </style>
</head>
<body>
  ${printArea.innerHTML}
</body>
</html>`);
  printWindow.document.close();
  setTimeout(() => { printWindow.print(); }, 300);
}
