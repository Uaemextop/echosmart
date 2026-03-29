/**
 * @file dht22_driver.cpp
 * @brief DHT22 (AM2302) temperature + humidity sensor implementation.
 */

#include "dht22_driver.h"

#include "../shared/logger.h"

namespace echosmart {

std::string DHT22Driver::sensor_type() const { return "dht22"; }
std::string DHT22Driver::protocol()    const { return "gpio"; }

double DHT22Driver::last_humidity() const { return last_humidity_; }

SensorData DHT22Driver::read(bool simulate) {
    if (!simulate) {
        log_warning(
            "DHT22: direct GPIO read is not implemented in C++; "
            "falling back to simulated data. "
            "Use the Python pigpio-based reader for real hardware.");
    }

    const double temperature = simulate_value(15.0, 35.0);
    const double humidity    = simulate_value(40.0, 90.0);
    last_humidity_           = humidity;

    return SensorData{
        /* sensor_type     */ "dht22",
        /* sensor_name     */ "DHT22 (sim)",
        /* value           */ temperature,
        /* unit            */ "°C",
        /* timestamp_ms    */ now_ms(),
        /* is_valid        */ true,
        /* secondary_value */ humidity,
        /* secondary_unit  */ "%"};
}

} // namespace echosmart
