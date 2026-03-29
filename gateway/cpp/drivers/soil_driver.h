/**
 * @file soil_driver.h
 * @brief Driver for a capacitive soil-moisture sensor read via ADS1115 ADC.
 *
 * The raw ADC value is linearly mapped between a "dry" and a "wet"
 * calibration point to produce a 0 – 100 % moisture percentage.
 * Default calibration values are provided but can be overridden with
 * calibrate().
 */

#pragma once

#include <string>

#include "sensor_driver.h"

namespace echosmart {

class SoilDriver : public SensorDriver {
public:
    SensorData  read(bool simulate) override;
    std::string sensor_type() const override;
    std::string protocol()    const override;

    /// Store two-point calibration for raw ADC → percentage conversion.
    /// @param dry_raw  ADC reading when the sensor is completely dry.
    /// @param wet_raw  ADC reading when the sensor is submerged in water.
    void calibrate(int dry_raw, int wet_raw);

    /// Convert a raw ADC integer to a moisture percentage using the
    /// stored calibration.  The result is clamped to [0, 100].
    double raw_to_percent(int raw) const;

private:
    int dry_raw_ = 21000;   ///< typical ADS1115 reading for dry air
    int wet_raw_ =  8500;   ///< typical ADS1115 reading for water
};

} // namespace echosmart
