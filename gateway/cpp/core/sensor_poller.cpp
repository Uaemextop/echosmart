/**
 * @file sensor_poller.cpp
 * @brief Implementation of the SensorPoller.
 */

#include "sensor_poller.h"

#include "../drivers/driver_factory.h"
#include "../shared/logger.h"

namespace echosmart {

SensorData SensorPoller::poll(const SensorEntry& entry, bool simulate) {
    auto driver = DriverFactory::create(entry.type);
    if (!driver) {
        log_error("No driver for sensor type: " + entry.type);
        return SensorData::empty(entry.type, "unknown driver");
    }

    SensorData reading = driver->read(simulate);
    reading.sensor_name = entry.name;
    return reading;
}

std::vector<SensorData> SensorPoller::poll_all(
        const std::vector<SensorEntry>& entries, bool simulate) {

    std::vector<SensorData> results;
    results.reserve(entries.size());

    for (const auto& entry : entries) {
        SensorData reading = poll(entry, simulate);

        if (reading.is_valid) {
            log_debug("Polled " + entry.name + " (" + entry.type + "): "
                      + std::to_string(reading.value) + " " + reading.unit);
        } else {
            log_warning("Failed to poll " + entry.name + " (" + entry.type + ")");
        }

        results.push_back(std::move(reading));
    }

    return results;
}

} // namespace echosmart
