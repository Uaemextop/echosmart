/**
 * @file mhz19c_driver.h
 * @brief Driver for the MH-Z19C NDIR CO₂ sensor (UART interface).
 *
 * The sensor communicates at 9600 baud, 8N1.  A full warm-up period
 * of ~3 minutes is required before readings are reliable.
 */

#pragma once

#include <chrono>
#include <string>

#include "sensor_driver.h"

namespace echosmart {

class MHZ19CDriver : public SensorDriver {
public:
    MHZ19CDriver();

    SensorData  read(bool simulate) override;
    std::string sensor_type() const override;
    std::string protocol()    const override;

    /// Send the zero-point (400 ppm) calibration command over UART.
    /// Returns true on success (stubbed to always return false for now).
    bool send_calibration();

    /// Returns true when enough time has elapsed since construction
    /// for the sensor's readings to be reliable (≥ 180 s).
    bool is_warmed_up() const;

private:
    using Clock     = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    TimePoint construction_time_;

    static constexpr int kWarmupSeconds = 180;
};

} // namespace echosmart
