/**
 * @file test_config_loader.cpp
 * @brief Tests for GatewayConfig and SensorEntry loaders.
 */

#include "test_helpers.h"
#include "../shared/config_loader.h"

using namespace echosmart;

TEST(load_nonexistent_returns_defaults) {
    auto cfg = GatewayConfig::load("/nonexistent/path/.env");
    ASSERT_EQ(cfg.gateway_id, std::string("gw-001"));
    ASSERT_EQ(cfg.gateway_name, std::string("EchoSmart Gateway"));
    ASSERT_EQ(cfg.mqtt_port, 1883);
    ASSERT_EQ(cfg.simulation_mode, false);
    ASSERT_EQ(cfg.log_level, std::string("INFO"));
}

TEST(load_sensors_nonexistent_returns_defaults) {
    auto sensors = SensorEntry::load_sensors("/nonexistent/sensors.json");
    ASSERT_TRUE(sensors.size() >= 3);
    // The default list should contain at least ds18b20 and dht22
    bool has_ds18b20 = false;
    bool has_dht22   = false;
    for (const auto& s : sensors) {
        if (s.type == "ds18b20") has_ds18b20 = true;
        if (s.type == "dht22")   has_dht22   = true;
    }
    ASSERT_TRUE(has_ds18b20);
    ASSERT_TRUE(has_dht22);
}

TEST(defaults_are_sensible) {
    auto cfg = GatewayConfig::load("/nonexistent/.env");
    ASSERT_TRUE(cfg.polling_interval > 0);
    ASSERT_TRUE(cfg.sync_interval > 0);
    ASSERT_TRUE(cfg.mqtt_port > 0);
    ASSERT_FALSE(cfg.gateway_id.empty());
    ASSERT_FALSE(cfg.cloud_api_url.empty());
}

int main() {
    std::cout << "test_config_loader\n";
    RUN_TEST(load_nonexistent_returns_defaults);
    RUN_TEST(load_sensors_nonexistent_returns_defaults);
    RUN_TEST(defaults_are_sensible);
    std::cout << "[PASS] test_config_loader\n";
    return 0;
}
