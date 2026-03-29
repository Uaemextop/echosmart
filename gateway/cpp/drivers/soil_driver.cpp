/**
 * @file soil_driver.cpp
 * @brief Capacitive soil-moisture sensor (ADS1115 ADC) implementation.
 */

#include "soil_driver.h"

#include <algorithm>

#include "../shared/logger.h"

namespace echosmart {

std::string SoilDriver::sensor_type() const { return "soil_moisture"; }
std::string SoilDriver::protocol()    const { return "i2c"; }

void SoilDriver::calibrate(int dry_raw, int wet_raw) {
    if (dry_raw == wet_raw) {
        log_error("SoilDriver: dry and wet calibration values must differ");
        return;
    }
    dry_raw_ = dry_raw;
    wet_raw_ = wet_raw;
    log_info("SoilDriver: calibrated (dry=" + std::to_string(dry_raw) +
             ", wet=" + std::to_string(wet_raw) + ")");
}

double SoilDriver::raw_to_percent(int raw) const {
    // Linear interpolation: 100 % at wet_raw_, 0 % at dry_raw_.
    const double range   = static_cast<double>(dry_raw_ - wet_raw_);
    const double percent = (static_cast<double>(dry_raw_ - raw) / range) * 100.0;
    return std::clamp(percent, 0.0, 100.0);
}

SensorData SoilDriver::read(bool simulate) {
    if (!simulate) {
        log_warning(
            "SoilDriver: ADS1115 I2C read is not yet implemented; "
            "returning simulated data.");
    }

    const double moisture = simulate_value(10.0, 95.0);

    return SensorData{
        /* sensor_type     */ "soil_moisture",
        /* sensor_name     */ "Soil Moisture (sim)",
        /* value           */ moisture,
        /* unit            */ "%",
        /* timestamp_ms    */ now_ms(),
        /* is_valid        */ true,
        /* secondary_value */ 0.0,
        /* secondary_unit  */ ""};
}

} // namespace echosmart
