/**
 * @file sensor_data.h
 * @brief Domain model for a single sensor reading.
 *
 * SensorData is the canonical in-memory representation passed between
 * drivers, the gateway daemon, alert evaluation, and JSON serialisation.
 * It supports dual-value sensors such as the DHT22 (temperature + humidity).
 */

#pragma once

#include <cstdint>
#include <string>

namespace echosmart {

struct SensorData {
    std::string sensor_type;       ///< e.g. "ds18b20", "dht22", "bh1750"
    std::string sensor_name;       ///< human-readable label
    double      value       = 0.0; ///< primary measurement
    std::string unit;              ///< e.g. "°C", "lux", "ppm"
    int64_t     timestamp_ms = 0;  ///< epoch milliseconds of the reading
    bool        is_valid     = false;

    // --- Secondary value (e.g. DHT22 humidity alongside temperature) ---
    double      secondary_value = 0.0;
    std::string secondary_unit;

    // ------------------------------------------------------------------
    // Serialisation
    // ------------------------------------------------------------------

    /// Serialise this reading to a JSON string using json_formatter.
    std::string to_json() const;

    /// Deserialise a JSON string produced by to_json().
    /// Returns an invalid SensorData if parsing fails.
    static SensorData from_json(const std::string& json);

    // ------------------------------------------------------------------
    // Factory helpers
    // ------------------------------------------------------------------

    /// Create an invalid/empty reading, typically used to report errors.
    static SensorData empty(const std::string& type, const std::string& error_msg);
};

} // namespace echosmart
