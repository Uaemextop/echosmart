/**
 * EchoSmart — Invernadero Inteligente
 * Interactive dashboard & landing page logic
 */

(function () {
  'use strict';

  // ========== MOBILE NAV TOGGLE ==========
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });
  }

  // ========== HERO CHART BARS ==========
  var heroChart = document.getElementById('heroChart');
  if (heroChart) {
    var hours = 24;
    for (var i = 0; i < hours; i++) {
      var bar = document.createElement('div');
      bar.className = 'chart-bar ' + (i % 2 === 0 ? 'green' : 'blue');
      var h = 20 + Math.floor(60 * Math.abs(Math.sin(i * 0.5 + 0.3)));
      bar.style.height = h + '%';
      heroChart.appendChild(bar);
    }
  }

  // ========== DASHBOARD: SIMULATED DATA ==========
  var lastUpdate = document.getElementById('lastUpdate');
  var tempValue = document.getElementById('tempValue');
  var humValue = document.getElementById('humValue');
  var luxValue = document.getElementById('luxValue');

  function formatTime(d) {
    return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  function randomVariation(base, range) {
    return base + (Math.random() - 0.5) * range;
  }

  function formatNumber(n) {
    return n.toLocaleString('es-MX', { maximumFractionDigits: 1 });
  }

  function updateSensorValues() {
    if (!tempValue) return;

    var temp = randomVariation(25.3, 2);
    var hum = randomVariation(68.5, 5);
    var lux = randomVariation(12450, 2000);
    var soil = randomVariation(55, 8);
    var co2 = randomVariation(820, 100);

    tempValue.textContent = formatNumber(temp) + '°C';
    humValue.textContent = formatNumber(hum) + '%';
    luxValue.textContent = formatNumber(Math.round(lux)) + ' lx';

    var sDS18B20 = document.getElementById('sDS18B20');
    var sDHT22 = document.getElementById('sDHT22');
    var sBH1750 = document.getElementById('sBH1750');
    var sSoil = document.getElementById('sSoil');
    var sMHZ19C = document.getElementById('sMHZ19C');

    if (sDS18B20) sDS18B20.textContent = formatNumber(temp) + '°C';
    if (sDHT22) sDHT22.textContent = formatNumber(randomVariation(22.1, 1.5)) + '°C / ' + formatNumber(hum) + '%';
    if (sBH1750) sBH1750.textContent = formatNumber(Math.round(lux)) + ' lx';
    if (sSoil) sSoil.textContent = formatNumber(soil) + '%';
    if (sMHZ19C) sMHZ19C.textContent = formatNumber(Math.round(co2)) + ' ppm';

    if (lastUpdate) lastUpdate.textContent = formatTime(new Date());
  }

  // Update every 3 seconds
  if (tempValue) {
    updateSensorValues();
    setInterval(updateSensorValues, 3000);
  }

  // ========== DASHBOARD: CANVAS CHARTS ==========
  var chartTempHum = document.getElementById('chartTempHum');
  var chartCO2Lux = document.getElementById('chartCO2Lux');

  function generateData(base, variance, count) {
    var data = [];
    for (var i = 0; i < count; i++) {
      data.push(base + Math.sin(i * 0.4) * variance * 0.6 + (Math.random() - 0.5) * variance * 0.4);
    }
    return data;
  }

  function drawLineChart(canvas, datasets, labels) {
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    var w = rect.width;
    var h = rect.height;

    var padding = { top: 20, right: 16, bottom: 30, left: 45 };
    var chartW = w - padding.left - padding.right;
    var chartH = h - padding.top - padding.bottom;

    // Background
    ctx.fillStyle = '#FAFAFA';
    ctx.fillRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = '#E0E0E0';
    ctx.lineWidth = 0.5;
    for (var i = 0; i <= 4; i++) {
      var gy = padding.top + (chartH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, gy);
      ctx.lineTo(w - padding.right, gy);
      ctx.stroke();
    }

    // Find global min/max
    var allVals = [];
    datasets.forEach(function (ds) { allVals = allVals.concat(ds.data); });
    var minVal = Math.min.apply(null, allVals);
    var maxVal = Math.max.apply(null, allVals);
    var range = maxVal - minVal || 1;
    minVal -= range * 0.1;
    maxVal += range * 0.1;
    range = maxVal - minVal;

    // Y-axis labels
    ctx.fillStyle = '#9E9E9E';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'right';
    for (var i = 0; i <= 4; i++) {
      var val = maxVal - (range / 4) * i;
      var gy = padding.top + (chartH / 4) * i;
      ctx.fillText(val.toFixed(1), padding.left - 6, gy + 3);
    }

    // X-axis labels
    ctx.textAlign = 'center';
    var step = Math.max(1, Math.floor(labels.length / 8));
    for (var i = 0; i < labels.length; i += step) {
      var lx = padding.left + (chartW / (labels.length - 1)) * i;
      ctx.fillText(labels[i], lx, h - 6);
    }

    // Draw datasets
    datasets.forEach(function (ds) {
      var pts = ds.data;
      ctx.strokeStyle = ds.color;
      ctx.lineWidth = 2;
      ctx.lineJoin = 'round';
      ctx.beginPath();
      for (var j = 0; j < pts.length; j++) {
        var px = padding.left + (chartW / (pts.length - 1)) * j;
        var py = padding.top + chartH - ((pts[j] - minVal) / range) * chartH;
        if (j === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      }
      ctx.stroke();

      // Fill area
      ctx.globalAlpha = 0.08;
      ctx.fillStyle = ds.color;
      ctx.lineTo(padding.left + chartW, padding.top + chartH);
      ctx.lineTo(padding.left, padding.top + chartH);
      ctx.closePath();
      ctx.fill();
      ctx.globalAlpha = 1;

      // Dots
      for (var j = 0; j < pts.length; j++) {
        var px = padding.left + (chartW / (pts.length - 1)) * j;
        var py = padding.top + chartH - ((pts[j] - minVal) / range) * chartH;
        ctx.fillStyle = ds.color;
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Legend
    var lx = padding.left + 10;
    var ly = padding.top + 2;
    datasets.forEach(function (ds, idx) {
      ctx.fillStyle = ds.color;
      ctx.fillRect(lx, ly, 12, 3);
      ctx.fillStyle = '#616161';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(ds.label, lx + 16, ly + 4);
      lx += ctx.measureText(ds.label).width + 36;
    });
  }

  function drawBarChart(canvas, datasets, labels) {
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    var w = rect.width;
    var h = rect.height;

    var padding = { top: 20, right: 16, bottom: 30, left: 50 };
    var chartW = w - padding.left - padding.right;
    var chartH = h - padding.top - padding.bottom;

    ctx.fillStyle = '#FAFAFA';
    ctx.fillRect(0, 0, w, h);

    var allVals = [];
    datasets.forEach(function (ds) { allVals = allVals.concat(ds.data); });
    var maxVal = Math.max.apply(null, allVals) * 1.15;

    // Grid
    ctx.strokeStyle = '#E0E0E0';
    ctx.lineWidth = 0.5;
    for (var i = 0; i <= 4; i++) {
      var gy = padding.top + (chartH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, gy);
      ctx.lineTo(w - padding.right, gy);
      ctx.stroke();
      ctx.fillStyle = '#9E9E9E';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';
      var val = maxVal - (maxVal / 4) * i;
      ctx.fillText(Math.round(val).toString(), padding.left - 6, gy + 3);
    }

    var groupW = chartW / labels.length;
    var barW = groupW / (datasets.length + 1);

    datasets.forEach(function (ds, di) {
      for (var j = 0; j < ds.data.length; j++) {
        var bh = (ds.data[j] / maxVal) * chartH;
        var bx = padding.left + groupW * j + barW * (di + 0.5);
        var by = padding.top + chartH - bh;
        ctx.fillStyle = ds.color;
        ctx.globalAlpha = 0.85;
        var radius = 3;
        ctx.beginPath();
        ctx.moveTo(bx, by + radius);
        ctx.arcTo(bx, by, bx + barW, by, radius);
        ctx.arcTo(bx + barW, by, bx + barW, by + bh, radius);
        ctx.lineTo(bx + barW, padding.top + chartH);
        ctx.lineTo(bx, padding.top + chartH);
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
      }
    });

    // X labels
    ctx.fillStyle = '#9E9E9E';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    for (var j = 0; j < labels.length; j++) {
      var lx = padding.left + groupW * j + groupW / 2;
      ctx.fillText(labels[j], lx, h - 6);
    }

    // Legend
    var lx = padding.left + 10;
    var ly = padding.top + 2;
    datasets.forEach(function (ds) {
      ctx.fillStyle = ds.color;
      ctx.fillRect(lx, ly, 12, 3);
      ctx.fillStyle = '#616161';
      ctx.textAlign = 'left';
      ctx.fillText(ds.label, lx + 16, ly + 4);
      lx += ctx.measureText(ds.label).width + 36;
    });
  }

  function renderCharts() {
    var hours = [];
    for (var i = 0; i < 24; i++) hours.push(i + ':00');

    drawLineChart(chartTempHum, [
      { label: 'Temperatura (°C)', color: '#2E7D32', data: generateData(25, 6, 24) },
      { label: 'Humedad (%)', color: '#1565C0', data: generateData(65, 12, 24) }
    ], hours);

    var periods = ['6:00', '8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00'];
    drawBarChart(chartCO2Lux, [
      { label: 'CO₂ (ppm)', color: '#FF8F00', data: generateData(800, 300, 8).map(Math.round) },
      { label: 'Lux (×100)', color: '#42A5F5', data: generateData(120, 50, 8).map(Math.round) }
    ], periods);
  }

  if (chartTempHum || chartCO2Lux) {
    renderCharts();
    window.addEventListener('resize', renderCharts);
    // Refresh charts every 10 seconds
    setInterval(renderCharts, 10000);
  }

  // Refresh button
  var btnRefresh = document.getElementById('btnRefresh');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', function () {
      updateSensorValues();
      renderCharts();
    });
  }

})();
