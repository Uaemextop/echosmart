/* ============================================
   EchoSmart — Dashboard JS
   ============================================ */

/* ---------- Demo Data ---------- */
const DEMO_SENSORS = [
  {
    id: 1, name: 'Temperatura Invernadero A', type: 'temp',
    value: 24.5, unit: '°C', status: 'ok', icon: '🌡️',
    color: 'var(--sensor-temp)', updated: 'Hace 1 min',
  },
  {
    id: 2, name: 'Humedad Invernadero A', type: 'humidity',
    value: 65, unit: '%', status: 'ok', icon: '💧',
    color: 'var(--sensor-humidity)', updated: 'Hace 1 min',
  },
  {
    id: 3, name: 'Luminosidad', type: 'light',
    value: 15200, unit: 'lux', status: 'warning', icon: '☀️',
    color: 'var(--sensor-light)', updated: 'Hace 2 min',
  },
  {
    id: 4, name: 'Humedad Suelo Zona 1', type: 'soil',
    value: 45, unit: '%', status: 'ok', icon: '🌱',
    color: 'var(--sensor-soil)', updated: 'Hace 3 min',
  },
  {
    id: 5, name: 'CO₂ Invernadero B', type: 'co2',
    value: 1200, unit: 'ppm', status: 'warning', icon: '💨',
    color: 'var(--sensor-co2)', updated: 'Hace 1 min',
  },
  {
    id: 6, name: 'Temperatura Invernadero B', type: 'temp',
    value: 28.1, unit: '°C', status: 'ok', icon: '🌡️',
    color: 'var(--sensor-temp)', updated: 'Hace 2 min',
  },
];

const DEMO_STATS = {
  totalSensors: 12,
  online: 10,
  activeAlerts: 3,
  lastReading: 'Hace 2 min',
};

const TEMP_HISTORY = [22, 23, 24, 25, 24.5, 23, 22.5, 24, 25.5, 26, 24.5, 23.8];
const HUMIDITY_HISTORY = [60, 62, 65, 68, 65, 63, 60, 58, 62, 65, 67, 64];
const CHART_LABELS = ['00:00','02:00','04:00','06:00','08:00','10:00','12:00','14:00','16:00','18:00','20:00','22:00'];

/* ---------- Render functions ---------- */
function renderStats() {
  const container = document.getElementById('stats-grid');
  if (!container) return;

  container.innerHTML = `
    <div class="card stat-card">
      <div class="stat-icon cyan">📡</div>
      <div>
        <div class="stat-value" id="stat-total">${DEMO_STATS.totalSensors}</div>
        <div class="stat-label">Total Sensores</div>
      </div>
    </div>
    <div class="card stat-card">
      <div class="stat-icon green">✅</div>
      <div>
        <div class="stat-value" id="stat-online">${DEMO_STATS.online}</div>
        <div class="stat-label">En Línea</div>
      </div>
    </div>
    <div class="card stat-card">
      <div class="stat-icon orange">⚠️</div>
      <div>
        <div class="stat-value" id="stat-alerts">${DEMO_STATS.activeAlerts}</div>
        <div class="stat-label">Alertas Activas</div>
      </div>
    </div>
    <div class="card stat-card">
      <div class="stat-icon blue">🕐</div>
      <div>
        <div class="stat-value" style="font-size:1.2rem" id="stat-last">${DEMO_STATS.lastReading}</div>
        <div class="stat-label">Última Lectura</div>
      </div>
    </div>
  `;
}

function renderSensors() {
  const container = document.getElementById('sensors-grid');
  if (!container) return;

  container.innerHTML = DEMO_SENSORS.map(s => `
    <div class="card sensor-card" data-sensor-id="${s.id}">
      <div class="sensor-header">
        <span class="sensor-name">
          <span>${s.icon}</span>
          ${s.name}
        </span>
        <span class="sensor-status ${s.status}"></span>
      </div>
      <div class="sensor-reading" style="color:${s.color}">
        <span class="sensor-value">${formatNumber(s.value)}</span>
        <span class="sensor-unit">${s.unit}</span>
      </div>
      <div class="sensor-meta">Actualizado: ${s.updated}</div>
    </div>
  `).join('');
}

function renderCharts() {
  renderBarChart('chart-temp', TEMP_HISTORY, CHART_LABELS, 'var(--sensor-temp)', 15, 35);
  renderBarChart('chart-humidity', HUMIDITY_HISTORY, CHART_LABELS, 'var(--sensor-humidity)', 0, 100);
}

function renderBarChart(containerId, data, labels, color, min, max) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const range = max - min;

  const barsHtml = data.map((v, i) => {
    const pct = Math.max(5, ((v - min) / range) * 100);
    return `<div class="chart-bar" style="height:${pct}%;background:${color};opacity:${0.5 + (i / data.length) * 0.5}" data-value="${v}"></div>`;
  }).join('');

  const labelsHtml = labels.map(l => `<span>${l}</span>`).join('');

  container.innerHTML = `
    <div class="chart-bars">${barsHtml}</div>
    <div class="chart-labels">${labelsHtml}</div>
  `;
}

/* ---------- User info ---------- */
function renderUserInfo() {
  const user = getUser();
  const nameEl = document.getElementById('user-name');
  const avatarEl = document.getElementById('user-avatar');

  if (user && nameEl) nameEl.textContent = user.name || user.email || 'Usuario';
  if (user && avatarEl) {
    const initials = (user.name || 'U').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    avatarEl.textContent = initials;
  }
}

/* ---------- Clock ---------- */
function startClock() {
  const el = document.getElementById('dashboard-clock');
  if (!el) return;

  function update() {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
  update();
  setInterval(update, 1000);
}

/* ---------- Simulate sensor updates ---------- */
function startSensorSimulation() {
  setInterval(() => {
    DEMO_SENSORS.forEach(sensor => {
      const variation = (Math.random() - 0.5) * 2;
      sensor.value = +(sensor.value + variation).toFixed(1);

      if (sensor.type === 'humidity' || sensor.type === 'soil') {
        sensor.value = Math.max(0, Math.min(100, sensor.value));
      }
      if (sensor.type === 'temp') {
        sensor.value = Math.max(10, Math.min(45, sensor.value));
      }
      if (sensor.type === 'light') {
        sensor.value = Math.max(0, Math.round(sensor.value));
      }
      if (sensor.type === 'co2') {
        sensor.value = Math.max(300, Math.round(sensor.value));
      }

      const el = document.querySelector(`[data-sensor-id="${sensor.id}"] .sensor-value`);
      if (el) el.textContent = formatNumber(sensor.value);
    });
  }, 5000);
}

/* ---------- Sidebar toggle ---------- */
function initSidebar() {
  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (!toggle || !sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  toggle.addEventListener('click', () => {
    if (sidebar.classList.contains('open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close sidebar on link click (mobile)
  sidebar.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 1024) closeSidebar();
    });
  });
}

/* ---------- Logout ---------- */
function initLogout() {
  const btn = document.getElementById('logout-btn');
  if (btn) btn.addEventListener('click', (e) => { e.preventDefault(); logout(); });
}

/* ---------- Helpers ---------- */
function formatNumber(n) {
  if (typeof n !== 'number') return n;
  if (n >= 1000) return n.toLocaleString('es-MX');
  if (Number.isInteger(n)) return n.toString();
  return n.toFixed(1);
}

/* ---------- Init ---------- */
document.addEventListener('DOMContentLoaded', () => {
  if (!requireAuth()) return;

  renderUserInfo();
  renderStats();
  renderSensors();
  renderCharts();
  startClock();
  startSensorSimulation();
  initSidebar();
  initLogout();
});
