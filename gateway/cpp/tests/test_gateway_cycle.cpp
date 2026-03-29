/**
 * @file test_gateway_cycle.cpp
 * @brief Tests for the Gateway lifecycle (run_once, poll_count, shutdown).
 */

#include "test_helpers.h"
#include "../core/gateway.h"
#include "../shared/config_loader.h"

using namespace echosmart;

TEST(run_once_completes) {
    GatewayConfig cfg;
    cfg.polling_interval = 1;
    cfg.simulation_mode  = true;

    std::vector<SensorEntry> sensors = {
        {"ds18b20", "Temp", "", -1, "", -1, ""}
    };

    Gateway gw(cfg, sensors, /*simulate=*/true);
    gw.run_once();  // Must not throw or crash.
    ASSERT_TRUE(true);
}

TEST(poll_count_increments) {
    GatewayConfig cfg;
    cfg.polling_interval = 1;

    std::vector<SensorEntry> sensors = {
        {"ds18b20", "Temp", "", -1, "", -1, ""}
    };

    Gateway gw(cfg, sensors, true);
    ASSERT_EQ(gw.poll_count(), 0);
    gw.run_once();
    ASSERT_EQ(gw.poll_count(), 1);
    gw.run_once();
    ASSERT_EQ(gw.poll_count(), 2);
}

TEST(empty_sensors_no_crash) {
    GatewayConfig cfg;
    cfg.polling_interval = 1;

    std::vector<SensorEntry> sensors;  // empty

    Gateway gw(cfg, sensors, true);
    gw.run_once();  // Must not crash.
    ASSERT_EQ(gw.poll_count(), 1);
}

TEST(shutdown_clears_running) {
    GatewayConfig cfg;
    cfg.polling_interval = 1;

    std::vector<SensorEntry> sensors;
    Gateway gw(cfg, sensors, true);

    ASSERT_FALSE(gw.is_running());
    gw.shutdown();
    ASSERT_FALSE(gw.is_running());
}

int main() {
    std::cout << "test_gateway_cycle\n";
    RUN_TEST(run_once_completes);
    RUN_TEST(poll_count_increments);
    RUN_TEST(empty_sensors_no_crash);
    RUN_TEST(shutdown_clears_running);
    std::cout << "[PASS] test_gateway_cycle\n";
    return 0;
}
