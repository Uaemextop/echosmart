/**
 * @file test_drivers.cpp
 * @brief Tests for DriverFactory and simulated sensor reads.
 */

#include "test_helpers.h"
#include "../drivers/driver_factory.h"

using namespace echosmart;

// -----------------------------------------------------------------------
// Factory creation tests
// -----------------------------------------------------------------------

TEST(create_ds18b20) {
    auto d = DriverFactory::create("ds18b20");
    ASSERT_NOT_NULL(d.get());
    ASSERT_EQ(d->sensor_type(), std::string("ds18b20"));
}

TEST(create_dht22) {
    auto d = DriverFactory::create("dht22");
    ASSERT_NOT_NULL(d.get());
    ASSERT_EQ(d->sensor_type(), std::string("dht22"));
}

TEST(create_bh1750) {
    auto d = DriverFactory::create("bh1750");
    ASSERT_NOT_NULL(d.get());
    ASSERT_EQ(d->sensor_type(), std::string("bh1750"));
}

TEST(create_soil_moisture) {
    auto d = DriverFactory::create("soil_moisture");
    ASSERT_NOT_NULL(d.get());
    ASSERT_EQ(d->sensor_type(), std::string("soil_moisture"));
}

TEST(create_mhz19c) {
    auto d = DriverFactory::create("mhz19c");
    ASSERT_NOT_NULL(d.get());
    ASSERT_EQ(d->sensor_type(), std::string("mhz19c"));
}

TEST(create_invalid_returns_null) {
    auto d = DriverFactory::create("invalid_sensor_xyz");
    ASSERT_NULL(d.get());
}

TEST(list_types_has_five) {
    auto types = DriverFactory::list_types();
    ASSERT_EQ(static_cast<int>(types.size()), 5);
}

// -----------------------------------------------------------------------
// Simulated read tests
// -----------------------------------------------------------------------

TEST(ds18b20_simulated_range) {
    auto d = DriverFactory::create("ds18b20");
    auto r = d->read(true);
    ASSERT_TRUE(r.is_valid);
    ASSERT_GE(r.value, 15.0);
    ASSERT_LE(r.value, 35.0);
    ASSERT_EQ(r.sensor_type, std::string("ds18b20"));
}

TEST(dht22_returns_secondary) {
    auto d = DriverFactory::create("dht22");
    auto r = d->read(true);
    ASSERT_TRUE(r.is_valid);
    ASSERT_GE(r.value, 15.0);
    ASSERT_LE(r.value, 35.0);
    ASSERT_TRUE(r.secondary_value > 0.0);
    ASSERT_FALSE(r.secondary_unit.empty());
}

TEST(bh1750_simulated_range) {
    auto d = DriverFactory::create("bh1750");
    auto r = d->read(true);
    ASSERT_TRUE(r.is_valid);
    ASSERT_GE(r.value, 100.0);
    ASSERT_LE(r.value, 50000.0);
}

TEST(soil_simulated_range) {
    auto d = DriverFactory::create("soil_moisture");
    auto r = d->read(true);
    ASSERT_TRUE(r.is_valid);
    ASSERT_GE(r.value, 10.0);
    ASSERT_LE(r.value, 95.0);
}

TEST(mhz19c_simulated_range) {
    auto d = DriverFactory::create("mhz19c");
    auto r = d->read(true);
    ASSERT_TRUE(r.is_valid);
    ASSERT_GE(r.value, 400.0);
    ASSERT_LE(r.value, 2000.0);
}

TEST(each_driver_valid_data) {
    auto types = DriverFactory::list_types();
    for (const auto& t : types) {
        auto d = DriverFactory::create(t);
        ASSERT_NOT_NULL(d.get());
        auto r = d->read(true);
        ASSERT_TRUE(r.is_valid);
        ASSERT_FALSE(r.unit.empty());
        ASSERT_TRUE(r.timestamp_ms > 0);
    }
}

int main() {
    std::cout << "test_drivers\n";
    RUN_TEST(create_ds18b20);
    RUN_TEST(create_dht22);
    RUN_TEST(create_bh1750);
    RUN_TEST(create_soil_moisture);
    RUN_TEST(create_mhz19c);
    RUN_TEST(create_invalid_returns_null);
    RUN_TEST(list_types_has_five);
    RUN_TEST(ds18b20_simulated_range);
    RUN_TEST(dht22_returns_secondary);
    RUN_TEST(bh1750_simulated_range);
    RUN_TEST(soil_simulated_range);
    RUN_TEST(mhz19c_simulated_range);
    RUN_TEST(each_driver_valid_data);
    std::cout << "[PASS] test_drivers\n";
    return 0;
}
