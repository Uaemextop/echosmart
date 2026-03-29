/**
 * @file bh1750_driver.h
 * @brief Driver for the BH1750 I²C ambient light sensor.
 *
 * The BH1750 communicates over I²C (default address 0x23, optional
 * 0x5C when ADDR is pulled high).  Real I²C access requires
 * ioctl(I2C_RDWR) on /dev/i2c-N; this implementation provides a
 * stub that logs a message and returns simulated data.
 */

#pragma once

#include <cstdint>
#include <string>

#include "sensor_driver.h"

namespace echosmart {

class BH1750Driver : public SensorDriver {
public:
    /// @param i2c_bus  Linux I²C bus number (default 1 → /dev/i2c-1).
    /// @param address  7-bit I²C address (default 0x23).
    explicit BH1750Driver(int i2c_bus = 1, uint8_t address = 0x23);

    SensorData  read(bool simulate) override;
    std::string sensor_type() const override;
    std::string protocol()    const override;

private:
    int     i2c_bus_;
    uint8_t address_;

    static constexpr double kMaxLux = 65535.0;
};

} // namespace echosmart
