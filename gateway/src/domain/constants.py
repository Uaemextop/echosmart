"""Domain constants — Business rules, thresholds, and sensor specifications.

All magic numbers and thresholds are centralized here so that business
logic never depends on hard-coded literals scattered across the codebase.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Sensor measurement ranges (physical hardware limits)
# ---------------------------------------------------------------------------
SENSOR_RANGES: dict[str, dict] = {
    "temperature": {"min": -55.0, "max": 125.0, "unit": "°C"},
    "humidity": {"min": 0.0, "max": 100.0, "unit": "%"},
    "light": {"min": 0.0, "max": 65535.0, "unit": "lux"},
    "soil_moisture": {"min": 0.0, "max": 100.0, "unit": "%"},
    "co2": {"min": 0.0, "max": 5000.0, "unit": "ppm"},
}

# ---------------------------------------------------------------------------
# Optimal greenhouse ranges (for default alert rules)
# ---------------------------------------------------------------------------
GREENHOUSE_OPTIMAL: dict[str, dict] = {
    "temperature": {"min": 18.0, "max": 28.0},
    "humidity": {"min": 60.0, "max": 80.0},
    "light": {"min": 10000.0, "max": 30000.0},
    "soil_moisture": {"min": 50.0, "max": 80.0},
    "co2": {"min": 400.0, "max": 1000.0},
}

# ---------------------------------------------------------------------------
# Simulation ranges (for drivers in simulation mode)
# ---------------------------------------------------------------------------
SIMULATION_RANGES: dict[str, dict] = {
    "temperature": {"min": 15.0, "max": 35.0},
    "humidity": {"min": 40.0, "max": 90.0},
    "light": {"min": 500.0, "max": 50000.0},
    "soil_moisture": {"min": 20.0, "max": 90.0},
    "co2": {"min": 350.0, "max": 2000.0},
}

# ---------------------------------------------------------------------------
# Driver timing constraints
# ---------------------------------------------------------------------------
DHT22_MIN_READ_INTERVAL_S = 2.0  # Hardware limitation: 0.5 Hz
DS18B20_MIN_READ_INTERVAL_S = 1.0  # Conversion time at 12-bit
MHZ19C_WARMUP_TIME_S = 180.0  # 3 minutes warm-up
MHZ19C_UART_TIMEOUT_S = 5.0

# ---------------------------------------------------------------------------
# Outlier filtering
# ---------------------------------------------------------------------------
DS18B20_MAX_DELTA_PER_SAMPLE = 5.0  # °C — discard if jump > 5 °C between reads

# ---------------------------------------------------------------------------
# Circuit breaker defaults
# ---------------------------------------------------------------------------
CIRCUIT_BREAKER_FAIL_THRESHOLD = 5  # consecutive failures to trip breaker
CIRCUIT_BREAKER_RECOVERY_S = 60  # seconds before retrying a tripped sensor

# ---------------------------------------------------------------------------
# Storage defaults
# ---------------------------------------------------------------------------
DEFAULT_RETENTION_DAYS = 7
DEFAULT_SYNC_BATCH_SIZE = 100

# ---------------------------------------------------------------------------
# Alert defaults
# ---------------------------------------------------------------------------
ALERT_COOLDOWN_S = 300  # Don't re-fire same alert within 5 minutes
ALERT_ESCALATION_S = 900  # Escalate unacknowledged alert after 15 minutes
