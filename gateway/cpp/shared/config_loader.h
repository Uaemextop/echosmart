/**
 * @file config_loader.h
 * @brief Configuration loaders for the EchoSmart gateway.
 *
 * Provides two loaders:
 *   1. GatewayConfig::load()   — parses a .env-style KEY=VALUE file.
 *   2. SensorEntry::load_sensors() — parses a sensors.json file.
 *
 * Both return sensible defaults when the source file is absent, so the
 * gateway can always start in simulation mode without configuration.
 */

#pragma once

#include <string>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// Gateway configuration (.env file)
// -----------------------------------------------------------------------

struct GatewayConfig {
    std::string gateway_id        = "gw-001";
    std::string gateway_name      = "EchoSmart Gateway";
    std::string cloud_api_url     = "http://localhost:8000";
    std::string cloud_api_key;
    std::string mqtt_broker       = "localhost";
    int         mqtt_port         = 1883;
    int         polling_interval  = 60;    ///< seconds between sensor polls
    int         sync_interval     = 300;   ///< seconds between cloud syncs
    bool        simulation_mode   = false;
    std::string log_level         = "INFO";

    /// Load configuration from a .env-style file at @p env_path.
    /// Lines starting with '#' and blank lines are ignored.
    /// Missing keys keep their default values.
    /// If the file does not exist, returns all defaults.
    static GatewayConfig load(const std::string& env_path);
};

// -----------------------------------------------------------------------
// Sensor inventory (sensors.json file)
// -----------------------------------------------------------------------

struct SensorEntry {
    std::string type;        ///< e.g. "ds18b20", "dht22"
    std::string name;        ///< human-readable label
    std::string device_id;   ///< 1-Wire device id for DS18B20
    int         pin      = -1;
    std::string address;     ///< I2C address for BH1750
    int         channel  = -1;
    std::string port;        ///< UART port for MH-Z19C

    /// Parse the sensor inventory from a JSON file.
    /// Returns a built-in default list if the file cannot be opened.
    static std::vector<SensorEntry> load_sensors(const std::string& json_path);
};

} // namespace echosmart
