/**
 * @file driver_factory.h
 * @brief Factory for instantiating sensor drivers by type name.
 *
 * Centralises the mapping from string identifiers (used in JSON
 * configuration and CLI arguments) to concrete SensorDriver sub-classes.
 */

#pragma once

#include <memory>
#include <string>
#include <vector>

#include "sensor_driver.h"

namespace echosmart {

class DriverFactory {
public:
    DriverFactory() = delete;

    /// Create a sensor driver for the given @p type name.
    /// Returns nullptr if @p type is unrecognised.
    static std::unique_ptr<SensorDriver> create(const std::string& type);

    /// List every supported type identifier (sorted alphabetically).
    static std::vector<std::string> list_types();
};

} // namespace echosmart
