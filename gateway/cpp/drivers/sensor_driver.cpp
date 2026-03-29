/**
 * @file sensor_driver.cpp
 * @brief Default implementations for the SensorDriver base class.
 */

#include "sensor_driver.h"

#include <chrono>

namespace echosmart {

bool SensorDriver::is_available() const { return true; }

double SensorDriver::simulate_value(double lo, double hi) {
    std::uniform_real_distribution<double> dist(lo, hi);
    return dist(rng_);
}

int64_t SensorDriver::now_ms() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(
               system_clock::now().time_since_epoch())
        .count();
}

} // namespace echosmart
