/**
 * @file sensor_poller.h
 * @brief Polls configured sensors and returns readings.
 *
 * SensorPoller is a stateless collaborator: it creates drivers on demand
 * via DriverFactory and delegates the actual I/O to each driver.
 */

#pragma once

#include "../shared/config_loader.h"
#include "../shared/sensor_data.h"

#include <vector>

namespace echosmart {

class SensorPoller {
public:
    /// Read a single sensor entry.  Creates a driver, calls read(), and
    /// populates the SensorData.sensor_name from the entry.
    SensorData poll(const SensorEntry& entry, bool simulate);

    /// Poll every sensor in @p entries, logging and skipping any errors.
    std::vector<SensorData> poll_all(const std::vector<SensorEntry>& entries,
                                     bool simulate);
};

} // namespace echosmart
