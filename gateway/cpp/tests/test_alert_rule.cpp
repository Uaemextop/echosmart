/**
 * @file test_alert_rule.cpp
 * @brief Tests for AlertRule evaluation and default rule loading.
 */

#include "test_helpers.h"
#include "../shared/alert_rule.h"

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

TEST(gt_triggers_on_high_value) {
    AlertRule rule;
    rule.sensor_type = "ds18b20";
    rule.condition   = AlertCondition::GT;
    rule.threshold   = 40.0;

    auto reading = make_reading("ds18b20", 41.0);
    ASSERT_TRUE(rule.evaluate(reading));
}

TEST(lt_triggers_on_low_value) {
    AlertRule rule;
    rule.sensor_type = "ds18b20";
    rule.condition   = AlertCondition::LT;
    rule.threshold   = 5.0;

    auto reading = make_reading("ds18b20", 3.0);
    ASSERT_TRUE(rule.evaluate(reading));
}

TEST(gt_no_trigger_on_normal) {
    AlertRule rule;
    rule.sensor_type = "ds18b20";
    rule.condition   = AlertCondition::GT;
    rule.threshold   = 40.0;

    auto reading = make_reading("ds18b20", 25.0);
    ASSERT_FALSE(rule.evaluate(reading));
}

TEST(no_trigger_wrong_sensor) {
    AlertRule rule;
    rule.sensor_type = "ds18b20";
    rule.condition   = AlertCondition::GT;
    rule.threshold   = 40.0;

    auto reading = make_reading("bh1750", 50000.0);
    ASSERT_FALSE(rule.evaluate(reading));
}

TEST(no_trigger_invalid_reading) {
    AlertRule rule;
    rule.sensor_type = "ds18b20";
    rule.condition   = AlertCondition::GT;
    rule.threshold   = 40.0;

    SensorData d;
    d.sensor_type = "ds18b20";
    d.value       = 50.0;
    d.is_valid    = false;
    ASSERT_FALSE(rule.evaluate(d));
}

TEST(load_defaults_has_enough_rules) {
    auto rules = AlertRule::load_defaults();
    ASSERT_GE(static_cast<int>(rules.size()), 9);
}

TEST(default_rules_have_valid_fields) {
    auto rules = AlertRule::load_defaults();
    for (const auto& r : rules) {
        ASSERT_FALSE(r.sensor_type.empty());
        ASSERT_FALSE(r.message.empty());
        // severity must be one of the enum values
        auto sev = severity_to_string(r.severity);
        ASSERT_TRUE(sev == "INFO" || sev == "WARNING" || sev == "CRITICAL");
    }
}

int main() {
    std::cout << "test_alert_rule\n";
    RUN_TEST(gt_triggers_on_high_value);
    RUN_TEST(lt_triggers_on_low_value);
    RUN_TEST(gt_no_trigger_on_normal);
    RUN_TEST(no_trigger_wrong_sensor);
    RUN_TEST(no_trigger_invalid_reading);
    RUN_TEST(load_defaults_has_enough_rules);
    RUN_TEST(default_rules_have_valid_fields);
    std::cout << "[PASS] test_alert_rule\n";
    return 0;
}
