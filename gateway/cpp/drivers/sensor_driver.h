/**
 * @file sensor_driver.h
 * @brief Abstract base class for all EchoSmart sensor drivers.
 *
 * Every hardware sensor (DS18B20, DHT22, BH1750, etc.) implements this
 * interface.  The base class provides simulation helpers and a uniform
 * polymorphic API consumed by the gateway daemon and CLI tools.
 */

#pragma once

#include <memory>
#include <random>
#include <string>

#include "../shared/sensor_data.h"

namespace echosmart {

class SensorDriver {
public:
    virtual ~SensorDriver() = default;

    /// Read the sensor.  When @p simulate is true the driver returns a
    /// plausible random value instead of talking to real hardware.
    virtual SensorData read(bool simulate) = 0;

    /// Short identifier for the sensor type, e.g. "ds18b20".
    virtual std::string sensor_type() const = 0;

    /// Communication protocol, e.g. "1-wire", "i2c", "gpio", "uart".
    virtual std::string protocol() const = 0;

    /// Returns true when the underlying hardware is accessible.
    /// Default implementation always returns true (suitable for simulation).
    virtual bool is_available() const;

protected:
    /// Generate a uniformly distributed random double in [lo, hi].
    double simulate_value(double lo, double hi);

    /// Return the current epoch time in milliseconds.
    static int64_t now_ms();

private:
    std::mt19937 rng_{std::random_device{}()};
};

} // namespace echosmart
