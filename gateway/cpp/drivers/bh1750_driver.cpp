/**
 * @file bh1750_driver.cpp
 * @brief BH1750 I²C ambient light sensor implementation.
 */

#include "bh1750_driver.h"

#include <algorithm>
#include <iomanip>
#include <sstream>

#include "../shared/logger.h"

namespace echosmart {

BH1750Driver::BH1750Driver(int i2c_bus, uint8_t address)
    : i2c_bus_(i2c_bus), address_(address) {}

std::string BH1750Driver::sensor_type() const { return "bh1750"; }
std::string BH1750Driver::protocol()    const { return "i2c"; }

SensorData BH1750Driver::read(bool simulate) {
    if (!simulate) {
        std::ostringstream addr_hex;
        addr_hex << "0x" << std::hex << std::setfill('0') << std::setw(2)
                 << static_cast<int>(address_);

        log_warning(
            "BH1750: I2C read on /dev/i2c-" +
            std::to_string(i2c_bus_) +
            " addr " + addr_hex.str() +
            " is not yet implemented; returning simulated data.");
    }

    double lux = simulate_value(100.0, 50000.0);

    // Clamp to the sensor's measurable range [0, 65535].
    lux = std::clamp(lux, 0.0, kMaxLux);

    return SensorData{
        /* sensor_type     */ "bh1750",
        /* sensor_name     */ "BH1750 (sim)",
        /* value           */ lux,
        /* unit            */ "lux",
        /* timestamp_ms    */ now_ms(),
        /* is_valid        */ (lux >= 0.0 && lux <= kMaxLux),
        /* secondary_value */ 0.0,
        /* secondary_unit  */ ""};
}

} // namespace echosmart
