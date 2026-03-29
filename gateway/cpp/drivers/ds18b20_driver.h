/**
 * @file ds18b20_driver.h
 * @brief Driver for the DS18B20 1-Wire digital temperature sensor.
 *
 * On Linux the kernel's w1-therm module exposes each probe as a file
 * under /sys/bus/w1/devices/28-XXXXXXXXXXXX/w1_slave.  The driver
 * parses the second line of that file to extract the temperature.
 */

#pragma once

#include <string>
#include <vector>

#include "sensor_driver.h"

namespace echosmart {

class DS18B20Driver : public SensorDriver {
public:
    SensorData  read(bool simulate) override;
    std::string sensor_type() const override;
    std::string protocol()    const override;
    bool        is_available() const override;

    /// Scan the 1-Wire bus and return all device IDs that start with "28-".
    static std::vector<std::string> list_devices();

private:
    static constexpr const char* kBusPath = "/sys/bus/w1/devices";

    static constexpr double kMinValid = -55.0;
    static constexpr double kMaxValid = 125.0;

    /// Read and parse a single w1_slave file.  Returns SensorData with
    /// is_valid == false when the CRC check fails or the file is missing.
    SensorData read_device(const std::string& device_id);
};

} // namespace echosmart
