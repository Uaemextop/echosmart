/**
 * @file alert_engine.h
 * @brief Evaluates sensor readings against alert rules with cooldown tracking.
 *
 * AlertEngine loads the default greenhouse thresholds and allows adding
 * custom rules.  It tracks per-rule cooldowns so that repeated alerts
 * within the cooldown window are suppressed.
 */

#pragma once

#include "../shared/alert_rule.h"
#include "../shared/sensor_data.h"

#include <cstdint>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace echosmart {

class AlertEngine {
public:
    /// Construct the engine and load default greenhouse rules.
    AlertEngine();

    /// Evaluate a reading against all rules.
    /// Returns pairs of (rule, reading) for every triggered alert
    /// whose cooldown has elapsed.
    std::vector<std::pair<AlertRule, SensorData>>
    evaluate(const SensorData& reading);

    /// Register an additional alert rule.
    void add_rule(const AlertRule& rule);

    /// Total number of alerts fired since construction.
    int triggered_count() const;

private:
    std::vector<AlertRule>         rules_;
    int                            triggered_count_{0};

    /// Maps a rule identity key to the epoch-seconds timestamp of the
    /// last time it fired.  Prevents re-firing within cooldown_seconds.
    std::map<std::string, int64_t> last_fired_;

    /// Build a unique key for a rule (sensor_type + condition + threshold).
    static std::string rule_key(const AlertRule& rule);
};

} // namespace echosmart
