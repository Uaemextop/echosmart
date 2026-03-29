/**
 * @file cmd_status.cpp
 * @brief Implementation of the "status" command.
 */

#include "cmd_status.h"

#include "../core/sensor_poller.h"
#include "../shared/config_loader.h"
#include "../shared/file_utils.h"
#include "../shared/json_formatter.h"
#include "../shared/logger.h"

#include <iostream>
#include <string>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// Output formatters
// -----------------------------------------------------------------------

static void print_status_json(const GatewayConfig& config,
                              const std::vector<SensorEntry>& sensors,
                              const std::vector<SensorData>& readings) {
    // Build sensors array.
    std::vector<std::string> sensor_items;
    sensor_items.reserve(sensors.size());
    for (const auto& s : sensors) {
        sensor_items.push_back(json_object({
            json_string("type", s.type),
            json_string("name", s.name)
        }));
    }

    // Build readings array.
    std::vector<std::string> reading_items;
    reading_items.reserve(readings.size());
    for (const auto& r : readings) {
        reading_items.push_back(r.to_json());
    }

    // Build top-level object.
    std::vector<std::string> fields;
    fields.push_back(json_string("gateway_id",   config.gateway_id));
    fields.push_back(json_string("gateway_name", config.gateway_name));
    fields.push_back(json_int("polling_interval", config.polling_interval));
    fields.push_back(json_bool("simulation_mode", config.simulation_mode));
    fields.push_back(json_int("sensor_count",
                              static_cast<int64_t>(sensors.size())));
    fields.push_back("\"sensors\":" + json_array(sensor_items));
    fields.push_back("\"readings\":" + json_array(reading_items));

    std::cout << json_object(fields) << "\n";
}

static void print_status_text(const GatewayConfig& config,
                              const std::vector<SensorEntry>& sensors,
                              const std::vector<SensorData>& readings) {
    std::cout << "=== EchoSmart Gateway Status ===\n"
              << "Gateway ID       : " << config.gateway_id << "\n"
              << "Gateway Name     : " << config.gateway_name << "\n"
              << "Polling Interval : " << config.polling_interval << "s\n"
              << "Simulation Mode  : "
                  << (config.simulation_mode ? "yes" : "no") << "\n"
              << "Sensors          : " << sensors.size() << " configured\n";

    if (!sensors.empty()) {
        std::cout << "\nConfigured sensors:\n";
        for (const auto& s : sensors) {
            std::cout << "  - " << s.name << " (" << s.type << ")\n";
        }
    }

    if (!readings.empty()) {
        std::cout << "\nLatest readings (simulated):\n";
        for (const auto& r : readings) {
            if (r.is_valid) {
                std::cout << "  " << r.sensor_name << ": "
                          << r.value << " " << r.unit;
                if (!r.secondary_unit.empty()) {
                    std::cout << "  |  " << r.secondary_value
                              << " " << r.secondary_unit;
                }
                std::cout << "\n";
            } else {
                std::cout << "  " << r.sensor_name << ": ERROR\n";
            }
        }
    }
}

// -----------------------------------------------------------------------
// Command entry point
// -----------------------------------------------------------------------

int cmd_status(const CliArgs& args) {
    std::string config_path  = args.get("config",  "/etc/echosmart/gateway.env");
    std::string sensors_path = args.get("sensors", "/etc/echosmart/sensors.json");

    GatewayConfig config = GatewayConfig::load(config_path);
    std::vector<SensorEntry> sensors = SensorEntry::load_sensors(sensors_path);

    // Run a simulated poll cycle to show current readings.
    SensorPoller poller;
    std::vector<SensorData> readings = poller.poll_all(sensors, /*simulate=*/true);

    std::string format = args.get("format", "json");
    if (format == "text") {
        print_status_text(config, sensors, readings);
    } else {
        print_status_json(config, sensors, readings);
    }

    return 0;
}

} // namespace echosmart
