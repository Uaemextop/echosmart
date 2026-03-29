/**
 * @file cmd_read.cpp
 * @brief Implementation of the "read" command.
 */

#include "cmd_read.h"

#include "../drivers/driver_factory.h"
#include "../shared/logger.h"

#include <iostream>
#include <string>

namespace echosmart {

int cmd_read(const CliArgs& args) {
    const std::string& sensor_type = args.input;

    if (sensor_type.empty()) {
        std::cerr << "Error: sensor type required.\n"
                  << "Usage: echosmart read <sensor_type> [--simulate]\n"
                  << "Available types:";
        for (const auto& t : DriverFactory::list_types()) {
            std::cerr << " " << t;
        }
        std::cerr << "\n";
        return 1;
    }

    auto driver = DriverFactory::create(sensor_type);
    if (!driver) {
        std::cerr << "Error: unknown sensor type '" << sensor_type << "'.\n"
                  << "Available types:";
        for (const auto& t : DriverFactory::list_types()) {
            std::cerr << " " << t;
        }
        std::cerr << "\n";
        return 1;
    }

    bool simulate = args.get_bool("simulate", true);
    SensorData reading = driver->read(simulate);

    if (!reading.is_valid) {
        std::cerr << "Error: failed to read sensor '" << sensor_type << "'.\n";
        return 2;
    }

    std::cout << reading.to_json() << "\n";
    return 0;
}

} // namespace echosmart
