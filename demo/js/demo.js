/* ===================================================
   EchoSmart Demo — Simulated sensor data & charts
   =================================================== */

(function () {
  "use strict";

  /* --- Constants --- */
  var SENSOR_COLORS = {
    temperature: "#FF5252",
    humidity: "#42A5F5",
    light: "#FFD54F",
    soil: "#8D6E63",
    co2: "#78909C",
  };

  var OPTIMAL_RANGES = {
    temperature: { min: 18, max: 28, unit: "°C" },
    humidity: { min: 60, max: 80, unit: "%" },
    light: { min: 10000, max: 30000, unit: " lx" },
    soil: { min: 50, max: 80, unit: "%" },
    co2: { min: 400, max: 1000, unit: " ppm" },
  };

  /* --- Helpers --- */
  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  function clamp(val, min, max) {
    return Math.min(Math.max(val, min), max);
  }

  function formatNum(n, decimals) {
    if (decimals === undefined) decimals = 0;
    return n.toLocaleString("es-MX", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  /* --- Generate 24-hour sample data --- */
  function generate24hData(baseValue, variance, min, max) {
    var data = [];
    var value = baseValue;
    for (var i = 0; i < 24; i++) {
      value = clamp(value + rand(-variance, variance), min, max);
      data.push(Math.round(value * 10) / 10);
    }
    return data;
  }

  var LABELS_24H = [];
  var now = new Date();
  for (var h = 23; h >= 0; h--) {
    var d = new Date(now.getTime() - h * 3600000);
    LABELS_24H.push(
      d.getHours().toString().padStart(2, "0") + ":00"
    );
  }

  /* --- Chart defaults --- */
  Chart.defaults.color = "#78909C";
  Chart.defaults.borderColor = "rgba(255,255,255,0.04)";
  Chart.defaults.font.family =
    '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

  function chartBase(ctx, label, data, color, yMin, yMax) {
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: LABELS_24H,
        datasets: [
          {
            label: label,
            data: data,
            borderColor: color,
            backgroundColor: color + "1A",
            fill: true,
            tension: 0.35,
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: "index" },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#111111",
            titleColor: "#E0E0E0",
            bodyColor: "#E0E0E0",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            cornerRadius: 8,
            padding: 10,
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { maxTicksLimit: 8, font: { size: 11 } },
          },
          y: {
            min: yMin,
            max: yMax,
            grid: { color: "rgba(255,255,255,0.04)" },
            ticks: { font: { size: 11 } },
          },
        },
      },
    });
  }

  /* --- Init charts --- */
  var tempData = generate24hData(23.5, 1.5, 15, 35);
  var humData = generate24hData(68, 3, 40, 95);
  var lightData = generate24hData(18420, 3000, 0, 50000);
  var soilData = generate24hData(62, 2, 30, 90);
  var co2Data = generate24hData(620, 40, 350, 1200);

  var tempChart = chartBase(
    document.getElementById("tempChart"),
    "Temperatura (°C)",
    tempData,
    SENSOR_COLORS.temperature,
    10,
    40
  );

  var humChart = chartBase(
    document.getElementById("humChart"),
    "Humedad (%)",
    humData,
    SENSOR_COLORS.humidity,
    30,
    100
  );

  /* --- All-sensors chart --- */
  function createAllSensorsChart() {
    var ctx = document.getElementById("allSensorsChart");
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: LABELS_24H,
        datasets: [
          {
            label: "Temperatura (°C)",
            data: tempData,
            borderColor: SENSOR_COLORS.temperature,
            tension: 0.35,
            pointRadius: 0,
            borderWidth: 2,
            yAxisID: "y",
          },
          {
            label: "Humedad (%)",
            data: humData,
            borderColor: SENSOR_COLORS.humidity,
            tension: 0.35,
            pointRadius: 0,
            borderWidth: 2,
            yAxisID: "y1",
          },
          {
            label: "CO₂ (ppm)",
            data: co2Data,
            borderColor: SENSOR_COLORS.co2,
            tension: 0.35,
            pointRadius: 0,
            borderWidth: 2,
            yAxisID: "y2",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: "index" },
        plugins: {
          legend: {
            position: "top",
            labels: {
              boxWidth: 12,
              boxHeight: 12,
              borderRadius: 3,
              useBorderRadius: true,
              padding: 16,
              font: { size: 12 },
            },
          },
          tooltip: {
            backgroundColor: "#111111",
            titleColor: "#E0E0E0",
            bodyColor: "#E0E0E0",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            cornerRadius: 8,
            padding: 10,
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { maxTicksLimit: 8, font: { size: 11 } },
          },
          y: {
            type: "linear",
            position: "left",
            min: 10,
            max: 40,
            grid: { color: "rgba(255,255,255,0.04)" },
            ticks: {
              font: { size: 11 },
              callback: function (v) {
                return v + "°C";
              },
            },
          },
          y1: {
            type: "linear",
            position: "right",
            min: 30,
            max: 100,
            grid: { display: false },
            ticks: {
              font: { size: 11 },
              callback: function (v) {
                return v + "%";
              },
            },
          },
          y2: {
            display: false,
            min: 300,
            max: 1200,
          },
        },
      },
    });
  }

  var allChart = createAllSensorsChart();

  /* --- Live update simulation --- */
  var currentValues = {
    temperature: tempData[tempData.length - 1],
    humidity: humData[humData.length - 1],
    light: lightData[lightData.length - 1],
    soil: soilData[soilData.length - 1],
    co2: co2Data[co2Data.length - 1],
  };

  function updateSensorValues() {
    currentValues.temperature = clamp(
      currentValues.temperature + rand(-0.3, 0.3),
      15,
      35
    );
    currentValues.humidity = clamp(
      currentValues.humidity + rand(-1, 1),
      40,
      95
    );
    currentValues.light = clamp(
      currentValues.light + rand(-500, 500),
      0,
      50000
    );
    currentValues.soil = clamp(
      currentValues.soil + rand(-0.5, 0.5),
      30,
      90
    );
    currentValues.co2 = clamp(
      currentValues.co2 + rand(-10, 10),
      350,
      1200
    );

    /* Update DOM */
    var tempEl = document.getElementById("tempValue");
    var humEl = document.getElementById("humValue");
    var lightEl = document.getElementById("lightValue");
    var soilEl = document.getElementById("soilValue");
    var co2El = document.getElementById("co2Value");

    if (tempEl)
      tempEl.textContent =
        formatNum(currentValues.temperature, 1) + "°C";
    if (humEl)
      humEl.textContent = formatNum(currentValues.humidity, 0) + "%";
    if (lightEl)
      lightEl.textContent =
        formatNum(Math.round(currentValues.light)) + " lx";
    if (soilEl)
      soilEl.textContent = formatNum(currentValues.soil, 0) + "%";
    if (co2El)
      co2El.textContent =
        formatNum(Math.round(currentValues.co2)) + " ppm";

    /* Update range status */
    var cards = document.querySelectorAll(".summary-card");
    cards.forEach(function (card) {
      var sensor = card.getAttribute("data-sensor");
      if (!sensor) return;
      var range = OPTIMAL_RANGES[sensor];
      var value = currentValues[sensor];
      var rangeEl = card.querySelector(".summary-range");
      if (rangeEl) {
        if (value >= range.min && value <= range.max) {
          rangeEl.className = "summary-range optimal";
        } else {
          rangeEl.className = "summary-range warning";
        }
      }
    });
  }

  setInterval(updateSensorValues, 3000);

  /* --- Clock --- */
  function updateClock() {
    var timeEl = document.getElementById("currentTime");
    if (timeEl) {
      var n = new Date();
      timeEl.textContent =
        n.getHours().toString().padStart(2, "0") +
        ":" +
        n.getMinutes().toString().padStart(2, "0") +
        ":" +
        n.getSeconds().toString().padStart(2, "0");
    }
  }
  updateClock();
  setInterval(updateClock, 1000);

  /* --- Mobile sidebar --- */
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebarOverlay");
  var mobileMenuBtn = document.getElementById("mobileMenuBtn");

  function openSidebar() {
    if (sidebar) sidebar.classList.add("open");
    if (overlay) overlay.classList.add("active");
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("active");
  }

  if (mobileMenuBtn) mobileMenuBtn.addEventListener("click", openSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);

  /* --- Nav items (visual only) --- */
  var navItems = document.querySelectorAll(".nav-item[data-page]");
  navItems.forEach(function (item) {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      navItems.forEach(function (n) {
        n.classList.remove("active");
      });
      item.classList.add("active");
      closeSidebar();
    });
  });
})();
