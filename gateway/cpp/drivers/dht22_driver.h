/**
 * @file dht22_driver.h
 * @brief Driver for the DHT22 (AM2302) temperature and humidity sensor.
 *
 * The DHT22 uses a proprietary single-wire protocol over a GPIO pin.
 * Bit-banging GPIO from user-space C++ is unreliable and usually
 * requires a kernel driver or a dedicated library (pigpio, wiringPi).
 * This implementation provides full simulation support and logs a
 * warning when a real hardware read is requested.
 *
 * The driver populates both the primary value (temperature in °C)
 * and the secondary value (relative humidity in %).
 */

#pragma once

#include <string>

#include "sensor_driver.h"

namespace echosmart {

class DHT22Driver : public SensorDriver {
public:
    SensorData  read(bool simulate) override;
    std::string sensor_type() const override;
    std::string protocol()    const override;

    /// Return the last humidity reading (secondary value).
    double last_humidity() const;

private:
    double last_humidity_ = 0.0;
};

} // namespace echosmart
