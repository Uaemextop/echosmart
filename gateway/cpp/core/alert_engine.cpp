/**
 * @file alert_engine.cpp
 * @brief Implementation of the AlertEngine with cooldown tracking.
 */

#include "alert_engine.h"

#include "../shared/logger.h"

#include <chrono>
#include <sstream>

namespace echosmart {

// -----------------------------------------------------------------------
// Construction
// -----------------------------------------------------------------------

AlertEngine::AlertEngine()
    : rules_(AlertRule::load_defaults()) {}

// -----------------------------------------------------------------------
// Rule identity key
// -----------------------------------------------------------------------

std::string AlertEngine::rule_key(const AlertRule& rule) {
    std::ostringstream oss;
    oss << rule.sensor_type
        << ":" << condition_to_string(rule.condition)
        << ":" << rule.threshold
        << ":" << rule.threshold_low
        << ":" << rule.threshold_high;
    return oss.str();
}

// -----------------------------------------------------------------------
// Current epoch seconds
// -----------------------------------------------------------------------

static int64_t epoch_seconds() {
    using namespace std::chrono;
    return duration_cast<seconds>(
        system_clock::now().time_since_epoch()
    ).count();
}

// -----------------------------------------------------------------------
// Evaluation
// -----------------------------------------------------------------------

std::vector<std::pair<AlertRule, SensorData>>
AlertEngine::evaluate(const SensorData& reading) {
    std::vector<std::pair<AlertRule, SensorData>> triggered;

    if (!reading.is_valid) return triggered;

    int64_t now = epoch_seconds();

    for (const auto& rule : rules_) {
        if (!rule.evaluate(reading)) continue;

        // Check cooldown.
        std::string key = rule_key(rule);
        auto it = last_fired_.find(key);
        if (it != last_fired_.end() && rule.cooldown_seconds > 0) {
            int64_t elapsed = now - it->second;
            if (elapsed < rule.cooldown_seconds) continue;
        }

        // Fire the alert.
        last_fired_[key] = now;
        ++triggered_count_;
        triggered.emplace_back(rule, reading);

        log_warning("[ALERT] " + severity_to_string(rule.severity)
                    + ": " + rule.message
                    + " (sensor=" + reading.sensor_type
                    + ", value=" + std::to_string(reading.value) + ")");
    }

    return triggered;
}

// -----------------------------------------------------------------------
// Mutators / accessors
// -----------------------------------------------------------------------

void AlertEngine::add_rule(const AlertRule& rule) {
    rules_.push_back(rule);
}

int AlertEngine::triggered_count() const {
    return triggered_count_;
}

} // namespace echosmart
