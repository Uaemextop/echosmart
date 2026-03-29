/**
 * @file cmd_calibrate.cpp
 * @brief Implementation of the "calibrate" command for soil moisture sensors.
 */

#include "cmd_calibrate.h"

#include "../shared/json_formatter.h"

#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>

namespace echosmart {

int cmd_calibrate(const CliArgs& args) {
    const std::string& sensor_type = args.input;

    if (sensor_type.empty()) {
        std::cerr << "Error: sensor type required.\n"
                  << "Usage: echosmart calibrate <sensor_type>"
                  << " --dry=<value> --wet=<value>\n"
                  << "Supported: soil\n";
        return 1;
    }

    if (sensor_type != "soil" && sensor_type != "soil_moisture") {
        std::cerr << "Error: calibration is only supported for 'soil'.\n";
        return 1;
    }

    if (!args.has("dry") || !args.has("wet")) {
        std::cerr << "Error: --dry and --wet ADC values are required.\n"
                  << "Usage: echosmart calibrate soil --dry=780 --wet=350\n";
        return 1;
    }

    int dry_value = args.get_int("dry", 0);
    int wet_value = args.get_int("wet", 0);

    if (dry_value == wet_value) {
        std::cerr << "Error: --dry and --wet values must be different.\n";
        return 1;
    }

    // Soil moisture: dry = high ADC, wet = low ADC (typical capacitive sensor).
    // Moisture% = (dry - raw) / (dry - wet) * 100
    double range = static_cast<double>(dry_value - wet_value);
    double scale = 100.0 / range;

    std::cout << "=== Soil Moisture Calibration ===\n"
              << "Dry value (0% moisture) : " << dry_value << "\n"
              << "Wet value (100% moisture): " << wet_value << "\n"
              << "\nMapping formula:\n"
              << "  moisture% = (" << dry_value << " - raw_adc) / "
              << std::fixed << std::setprecision(1) << range
              << " * 100\n"
              << "  scale factor: " << std::setprecision(4) << scale << "\n\n";

    // Demonstrate with a mid-range reading.
    int mid_raw = (dry_value + wet_value) / 2;
    double mid_pct = (static_cast<double>(dry_value - mid_raw) / range) * 100.0;
    std::cout << "Example: raw=" << mid_raw << " → "
              << std::setprecision(1) << mid_pct << "%\n";

    // Print JSON summary.
    std::cout << "\n" << json_object({
        json_string("sensor_type", "soil_moisture"),
        json_int("dry_value", dry_value),
        json_int("wet_value", wet_value),
        json_number("scale_factor", scale, 4),
        json_string("formula",
            "moisture = (" + std::to_string(dry_value)
            + " - raw) / " + std::to_string(dry_value - wet_value)
            + " * 100")
    }) << "\n";

    return 0;
}

} // namespace echosmart
