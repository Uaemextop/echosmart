/**
 * @file alert_rule.cpp
 * @brief Implementation of alert-rule evaluation and default thresholds.
 */

#include "alert_rule.h"

#include <cmath>

namespace echosmart {

// -----------------------------------------------------------------------
// Enum → string conversions
// -----------------------------------------------------------------------

std::string severity_to_string(AlertSeverity severity) {
    switch (severity) {
        case AlertSeverity::INFO:     return "INFO";
        case AlertSeverity::WARNING:  return "WARNING";
        case AlertSeverity::CRITICAL: return "CRITICAL";
    }
    return "UNKNOWN";
}

std::string condition_to_string(AlertCondition condition) {
    switch (condition) {
        case AlertCondition::GT:    return "GT";
        case AlertCondition::LT:    return "LT";
        case AlertCondition::EQ:    return "EQ";
        case AlertCondition::RANGE: return "RANGE";
    }
    return "UNKNOWN";
}

// -----------------------------------------------------------------------
// Evaluation
// -----------------------------------------------------------------------

static constexpr double kFloatEqualityEpsilon = 1e-9;

bool AlertRule::evaluate(const SensorData& reading) const {
    if (!reading.is_valid) return false;
    if (reading.sensor_type != sensor_type) return false;

    switch (condition) {
        case AlertCondition::GT:
            return reading.value > threshold;

        case AlertCondition::LT:
            return reading.value < threshold;

        case AlertCondition::EQ:
            return std::fabs(reading.value - threshold) < kFloatEqualityEpsilon;

        case AlertCondition::RANGE:
            return reading.value >= threshold_low
                && reading.value <= threshold_high;
    }

    return false;
}

// -----------------------------------------------------------------------
// Default greenhouse thresholds
// -----------------------------------------------------------------------

static AlertRule make_gt(const std::string& sensor, double threshold,
                         AlertSeverity severity, const std::string& msg,
                         int cooldown = 0) {
    AlertRule rule;
    rule.sensor_type      = sensor;
    rule.condition        = AlertCondition::GT;
    rule.threshold        = threshold;
    rule.severity         = severity;
    rule.message          = msg;
    rule.cooldown_seconds = cooldown;
    return rule;
}

static AlertRule make_lt(const std::string& sensor, double threshold,
                         AlertSeverity severity, const std::string& msg,
                         int cooldown = 0) {
    AlertRule rule;
    rule.sensor_type      = sensor;
    rule.condition        = AlertCondition::LT;
    rule.threshold        = threshold;
    rule.severity         = severity;
    rule.message          = msg;
    rule.cooldown_seconds = cooldown;
    return rule;
}

std::vector<AlertRule> AlertRule::load_defaults() {
    // Temperature thresholds (°C)
    constexpr double kTempCriticalHigh = 40.0;
    constexpr double kTempWarningLow   =  5.0;

    // Humidity thresholds (%)
    constexpr double kHumidityWarningHigh = 90.0;
    constexpr double kHumidityWarningLow  = 30.0;

    // Light threshold (lux)
    constexpr double kLightWarningHigh = 60000.0;

    // Soil moisture thresholds (%)
    constexpr double kSoilWarningLow  = 20.0;
    constexpr double kSoilWarningHigh = 95.0;

    // CO₂ thresholds (ppm)
    constexpr double kCo2CriticalHigh = 2000.0;
    constexpr double kCo2WarningHigh  = 1500.0;

    return {
        // DS18B20 — temperature
        make_gt("ds18b20", kTempCriticalHigh,
                AlertSeverity::CRITICAL, "Temperature above 40°C"),
        make_lt("ds18b20", kTempWarningLow,
                AlertSeverity::WARNING,  "Temperature below 5°C"),

        // DHT22 — humidity (secondary_value, but alert is on primary for now)
        make_gt("dht22", kHumidityWarningHigh,
                AlertSeverity::WARNING,  "Humidity above 90%"),
        make_lt("dht22", kHumidityWarningLow,
                AlertSeverity::WARNING,  "Humidity below 30%"),

        // BH1750 — light
        make_gt("bh1750", kLightWarningHigh,
                AlertSeverity::WARNING,  "Light level above 60000 lux"),

        // Soil moisture
        make_lt("soil_moisture", kSoilWarningLow,
                AlertSeverity::WARNING,  "Soil moisture below 20%"),
        make_gt("soil_moisture", kSoilWarningHigh,
                AlertSeverity::WARNING,  "Soil moisture above 95%"),

        // MH-Z19C — CO₂
        make_gt("mhz19c", kCo2CriticalHigh,
                AlertSeverity::CRITICAL, "CO2 above 2000 ppm"),
        make_gt("mhz19c", kCo2WarningHigh,
                AlertSeverity::WARNING,  "CO2 above 1500 ppm"),
    };
}

} // namespace echosmart
