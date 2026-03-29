/**
 * @file test_alert_engine.cpp
 * @brief Tests for AlertEngine evaluation, counting, and cooldown.
 */

#include "test_helpers.h"
#include "../core/alert_engine.h"

using namespace echosmart;

static SensorData make_reading(const std::string& type, double value) {
    SensorData d;
    d.sensor_type  = type;
    d.sensor_name  = "test";
    d.value        = value;
    d.unit         = "unit";
    d.timestamp_ms = 1000;
    d.is_valid     = true;
    return d;
}

TEST(evaluates_default_rules) {
    AlertEngine engine;
    // A normal temperature should not trigger any default ds18b20 rules.
    auto reading   = make_reading("ds18b20", 25.0);
    auto triggered = engine.evaluate(reading);
    ASSERT_TRUE(triggered.empty());
}

TEST(high_temp_triggers_critical) {
    AlertEngine engine;
    // Default rules: ds18b20 GT 40 => CRITICAL
    auto reading   = make_reading("ds18b20", 45.0);
    auto triggered = engine.evaluate(reading);
    ASSERT_FALSE(triggered.empty());

    bool found_critical = false;
    for (const auto& [rule, data] : triggered) {
        if (rule.severity == AlertSeverity::CRITICAL) found_critical = true;
    }
    ASSERT_TRUE(found_critical);
}

TEST(normal_temp_no_trigger) {
    AlertEngine engine;
    auto reading   = make_reading("ds18b20", 22.0);
    auto triggered = engine.evaluate(reading);
    ASSERT_TRUE(triggered.empty());
}

TEST(triggered_count_increments) {
    AlertEngine engine;
    ASSERT_EQ(engine.triggered_count(), 0);

    // Fire a high-temp alert.
    engine.evaluate(make_reading("ds18b20", 45.0));
    ASSERT_TRUE(engine.triggered_count() > 0);

    int before = engine.triggered_count();
    // Add a rule with no cooldown so it always fires.
    AlertRule rule;
    rule.sensor_type      = "bh1750";
    rule.condition         = AlertCondition::GT;
    rule.threshold         = 1.0;
    rule.severity          = AlertSeverity::INFO;
    rule.message           = "test";
    rule.cooldown_seconds  = 0;
    engine.add_rule(rule);

    engine.evaluate(make_reading("bh1750", 5000.0));
    ASSERT_TRUE(engine.triggered_count() > before);
}

TEST(cooldown_prevents_refire) {
    AlertEngine engine;

    // Add a custom rule with a long cooldown.
    AlertRule rule;
    rule.sensor_type      = "bh1750";
    rule.condition         = AlertCondition::GT;
    rule.threshold         = 100.0;
    rule.severity          = AlertSeverity::WARNING;
    rule.message           = "bright";
    rule.cooldown_seconds  = 9999;
    engine.add_rule(rule);

    // First evaluation should fire.
    auto r1 = engine.evaluate(make_reading("bh1750", 50000.0));
    bool first_fired = false;
    for (const auto& [r, d] : r1) {
        if (r.message == "bright") first_fired = true;
    }
    ASSERT_TRUE(first_fired);

    // Second evaluation within cooldown should NOT re-fire that rule.
    auto r2 = engine.evaluate(make_reading("bh1750", 50000.0));
    bool second_fired = false;
    for (const auto& [r, d] : r2) {
        if (r.message == "bright") second_fired = true;
    }
    ASSERT_FALSE(second_fired);
}

int main() {
    std::cout << "test_alert_engine\n";
    RUN_TEST(evaluates_default_rules);
    RUN_TEST(high_temp_triggers_critical);
    RUN_TEST(normal_temp_no_trigger);
    RUN_TEST(triggered_count_increments);
    RUN_TEST(cooldown_prevents_refire);
    std::cout << "[PASS] test_alert_engine\n";
    return 0;
}
