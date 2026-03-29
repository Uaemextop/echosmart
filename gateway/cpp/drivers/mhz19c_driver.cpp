/**
 * @file mhz19c_driver.cpp
 * @brief MH-Z19C NDIR CO₂ sensor (UART) implementation.
 */

#include "mhz19c_driver.h"

#include "../shared/logger.h"

namespace echosmart {

MHZ19CDriver::MHZ19CDriver()
    : construction_time_(Clock::now()) {}

std::string MHZ19CDriver::sensor_type() const { return "mhz19c"; }
std::string MHZ19CDriver::protocol()    const { return "uart"; }

bool MHZ19CDriver::is_warmed_up() const {
    using namespace std::chrono;
    const auto elapsed =
        duration_cast<seconds>(Clock::now() - construction_time_).count();
    return elapsed >= kWarmupSeconds;
}

bool MHZ19CDriver::send_calibration() {
    if (!is_warmed_up()) {
        log_warning("MHZ19C: sensor has not warmed up yet; "
                    "calibration request ignored.");
        return false;
    }

    log_warning("MHZ19C: UART calibration command is not yet "
                "implemented; returning false.");
    return false;
}

SensorData MHZ19CDriver::read(bool simulate) {
    if (!simulate) {
        log_warning(
            "MHZ19C: UART read is not yet implemented; "
            "returning simulated data.");
    }

    if (!is_warmed_up()) {
        log_warning("MHZ19C: sensor still warming up; "
                    "reading may be inaccurate.");
    }

    const double ppm = simulate_value(400.0, 2000.0);

    return SensorData{
        /* sensor_type     */ "mhz19c",
        /* sensor_name     */ "MH-Z19C (sim)",
        /* value           */ ppm,
        /* unit            */ "ppm",
        /* timestamp_ms    */ now_ms(),
        /* is_valid        */ true,
        /* secondary_value */ 0.0,
        /* secondary_unit  */ ""};
}

} // namespace echosmart
