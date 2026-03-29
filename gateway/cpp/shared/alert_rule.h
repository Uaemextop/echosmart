/**
 * @file alert_rule.h
 * @brief Alert-rule definitions and evaluation for the EchoSmart gateway.
 *
 * An AlertRule describes a threshold condition that, when met, fires an
 * alert of a given severity.  The static load_defaults() provides the
 * standard greenhouse thresholds (temperature, humidity, CO₂, light,
 * soil moisture).
 */

#pragma once

#include "sensor_data.h"

#include <cstdint>
#include <string>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------

enum class AlertSeverity {
    INFO,
    WARNING,
    CRITICAL
};

enum class AlertCondition {
    GT,     ///< value > threshold
    LT,     ///< value < threshold
    EQ,     ///< value == threshold (rarely used)
    RANGE   ///< threshold_low <= value <= threshold_high
};

// -----------------------------------------------------------------------
// Conversion helpers
// -----------------------------------------------------------------------

std::string severity_to_string(AlertSeverity severity);
std::string condition_to_string(AlertCondition condition);

// -----------------------------------------------------------------------
// AlertRule
// -----------------------------------------------------------------------

struct AlertRule {
    std::string    sensor_type;       ///< e.g. "ds18b20", "dht22"
    AlertCondition condition = AlertCondition::GT;
    double         threshold      = 0.0;   ///< used for GT, LT, EQ
    double         threshold_low  = 0.0;   ///< RANGE lower bound
    double         threshold_high = 0.0;   ///< RANGE upper bound
    AlertSeverity  severity  = AlertSeverity::WARNING;
    std::string    message;
    int            cooldown_seconds = 0;   ///< minimum gap between alerts

    /// Evaluate this rule against a sensor reading.
    /// Returns true if the condition is met (alert should fire).
    bool evaluate(const SensorData& reading) const;

    /// Load the built-in greenhouse alert thresholds.
    static std::vector<AlertRule> load_defaults();
};

} // namespace echosmart
