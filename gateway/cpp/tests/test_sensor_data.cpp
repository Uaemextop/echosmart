/**
 * @file test_sensor_data.cpp
 * @brief Tests for SensorData serialisation and factory helpers.
 */

#include "test_helpers.h"
#include "../shared/sensor_data.h"

using namespace echosmart;

TEST(to_json_produces_valid_json) {
    SensorData d;
    d.sensor_type  = "ds18b20";
    d.sensor_name  = "Temp A";
    d.value        = 23.45;
    d.unit         = "°C";
    d.timestamp_ms = 1711699200000LL;
    d.is_valid     = true;

    auto j = d.to_json();
    ASSERT_TRUE(j.front() == '{');
    ASSERT_TRUE(j.back() == '}');
    ASSERT_CONTAINS(j, "\"sensor_type\":\"ds18b20\"");
    ASSERT_CONTAINS(j, "\"sensor_name\":\"Temp A\"");
    ASSERT_CONTAINS(j, "\"value\":");
    ASSERT_CONTAINS(j, "\"unit\":");
    ASSERT_CONTAINS(j, "\"is_valid\":true");
}

TEST(from_json_parses_correctly) {
    SensorData d;
    d.sensor_type  = "bh1750";
    d.sensor_name  = "Light";
    d.value        = 5000.0;
    d.unit         = "lux";
    d.timestamp_ms = 1000LL;
    d.is_valid     = true;

    auto parsed = SensorData::from_json(d.to_json());
    ASSERT_EQ(parsed.sensor_type, std::string("bh1750"));
    ASSERT_EQ(parsed.sensor_name, std::string("Light"));
    ASSERT_NEAR(parsed.value, 5000.0, 0.1);
    ASSERT_EQ(parsed.is_valid, true);
}

TEST(empty_sets_invalid) {
    auto d = SensorData::empty("ds18b20", "test error");
    ASSERT_FALSE(d.is_valid);
    ASSERT_EQ(d.sensor_type, std::string("ds18b20"));
}

TEST(round_trip_preserves_data) {
    SensorData d;
    d.sensor_type  = "mhz19c";
    d.sensor_name  = "CO2 Zone";
    d.value        = 812.50;
    d.unit         = "ppm";
    d.timestamp_ms = 9999999LL;
    d.is_valid     = true;

    auto parsed = SensorData::from_json(d.to_json());
    ASSERT_EQ(parsed.sensor_type, std::string("mhz19c"));
    ASSERT_EQ(parsed.sensor_name, std::string("CO2 Zone"));
    ASSERT_NEAR(parsed.value, 812.50, 0.01);
    ASSERT_EQ(parsed.unit, std::string("ppm"));
    ASSERT_EQ(parsed.is_valid, true);
}

TEST(dht22_secondary_value) {
    SensorData d;
    d.sensor_type     = "dht22";
    d.sensor_name     = "DHT";
    d.value           = 22.5;
    d.unit            = "°C";
    d.secondary_value = 65.0;
    d.secondary_unit  = "%";
    d.timestamp_ms    = 1000LL;
    d.is_valid        = true;

    auto j = d.to_json();
    ASSERT_CONTAINS(j, "\"secondary_value\":");
    ASSERT_CONTAINS(j, "\"secondary_unit\":\"%\"");

    auto parsed = SensorData::from_json(j);
    ASSERT_NEAR(parsed.secondary_value, 65.0, 0.1);
    ASSERT_EQ(parsed.secondary_unit, std::string("%"));
}

int main() {
    std::cout << "test_sensor_data\n";
    RUN_TEST(to_json_produces_valid_json);
    RUN_TEST(from_json_parses_correctly);
    RUN_TEST(empty_sets_invalid);
    RUN_TEST(round_trip_preserves_data);
    RUN_TEST(dht22_secondary_value);
    std::cout << "[PASS] test_sensor_data\n";
    return 0;
}
