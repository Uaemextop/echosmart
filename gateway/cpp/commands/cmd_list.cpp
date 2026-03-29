/**
 * @file cmd_list.cpp
 * @brief Implementation of the "list" command — print configured sensors.
 */

#include "cmd_list.h"

#include "../shared/config_loader.h"
#include "../shared/json_formatter.h"

#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// Output formatters
// -----------------------------------------------------------------------

static void print_sensors_json(const std::vector<SensorEntry>& sensors) {
    std::vector<std::string> items;
    items.reserve(sensors.size());

    for (const auto& s : sensors) {
        std::vector<std::string> fields;
        fields.push_back(json_string("type", s.type));
        fields.push_back(json_string("name", s.name));

        if (!s.device_id.empty())
            fields.push_back(json_string("device_id", s.device_id));
        if (s.pin >= 0)
            fields.push_back(json_int("pin", s.pin));
        if (!s.address.empty())
            fields.push_back(json_string("address", s.address));
        if (s.channel >= 0)
            fields.push_back(json_int("channel", s.channel));
        if (!s.port.empty())
            fields.push_back(json_string("port", s.port));

        items.push_back(json_object(fields));
    }

    std::cout << json_array(items) << "\n";
}

static void print_sensors_text(const std::vector<SensorEntry>& sensors) {
    if (sensors.empty()) {
        std::cout << "No sensors configured.\n";
        return;
    }

    std::cout << "=== Configured Sensors ===\n\n";
    std::cout << std::left
              << std::setw(4)  << "#"
              << std::setw(16) << "Type"
              << std::setw(24) << "Name"
              << "Details\n";
    std::cout << std::string(60, '-') << "\n";

    int idx = 1;
    for (const auto& s : sensors) {
        std::string details;
        if (!s.device_id.empty()) details += "dev=" + s.device_id + " ";
        if (s.pin >= 0)           details += "pin=" + std::to_string(s.pin) + " ";
        if (!s.address.empty())   details += "addr=" + s.address + " ";
        if (s.channel >= 0)       details += "ch=" + std::to_string(s.channel) + " ";
        if (!s.port.empty())      details += "port=" + s.port + " ";

        std::cout << std::left
                  << std::setw(4)  << idx++
                  << std::setw(16) << s.type
                  << std::setw(24) << s.name
                  << details << "\n";
    }

    std::cout << "\nTotal: " << sensors.size() << " sensor(s)\n";
}

// -----------------------------------------------------------------------
// Command entry point
// -----------------------------------------------------------------------

int cmd_list(const CliArgs& args) {
    std::string sensors_path = args.get("sensors", "/etc/echosmart/sensors.json");
    std::vector<SensorEntry> sensors = SensorEntry::load_sensors(sensors_path);

    std::string format = args.get("format", "json");
    if (format == "text") {
        print_sensors_text(sensors);
    } else {
        print_sensors_json(sensors);
    }

    return 0;
}

} // namespace echosmart
