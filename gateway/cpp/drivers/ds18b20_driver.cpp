/**
 * @file ds18b20_driver.cpp
 * @brief DS18B20 1-Wire temperature sensor implementation.
 *
 * Kernel interface
 * ~~~~~~~~~~~~~~~~
 * /sys/bus/w1/devices/28-XXXXXXXXXXXX/w1_slave contains two lines:
 *
 *   73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
 *   73 01 4b 46 7f ff 0d 10 41 t=23187
 *
 * The driver checks for "YES" on the first line (valid CRC) and
 * extracts the integer after "t=" on the second line, dividing by
 * 1000 to obtain degrees Celsius.
 */

#include "ds18b20_driver.h"

#include <filesystem>

#include "../shared/file_utils.h"
#include "../shared/logger.h"

namespace fs = std::filesystem;

namespace echosmart {

// -----------------------------------------------------------------
// Public API
// -----------------------------------------------------------------

std::string DS18B20Driver::sensor_type() const { return "ds18b20"; }
std::string DS18B20Driver::protocol()    const { return "1-wire"; }

bool DS18B20Driver::is_available() const {
    return !list_devices().empty();
}

SensorData DS18B20Driver::read(bool simulate) {
    if (simulate) {
        return SensorData{
            /* sensor_type    */ "ds18b20",
            /* sensor_name    */ "DS18B20 (sim)",
            /* value          */ simulate_value(15.0, 35.0),
            /* unit           */ "°C",
            /* timestamp_ms   */ now_ms(),
            /* is_valid       */ true,
            /* secondary_value*/ 0.0,
            /* secondary_unit */ ""};
    }

    auto devices = list_devices();
    if (devices.empty()) {
        log_error("DS18B20: no 1-Wire devices found under " +
                  std::string(kBusPath));
        return SensorData::empty("ds18b20", "no devices found");
    }

    // Read the first available probe.
    return read_device(devices.front());
}

// -----------------------------------------------------------------
// Device enumeration
// -----------------------------------------------------------------

std::vector<std::string> DS18B20Driver::list_devices() {
    std::vector<std::string> ids;

    if (!fs::exists(kBusPath) || !fs::is_directory(kBusPath)) {
        return ids;
    }

    for (const auto& entry : fs::directory_iterator(kBusPath)) {
        const std::string name = entry.path().filename().string();
        if (name.rfind("28-", 0) == 0) {   // starts with "28-"
            ids.push_back(name);
        }
    }
    return ids;
}

// -----------------------------------------------------------------
// Single-device read
// -----------------------------------------------------------------

SensorData DS18B20Driver::read_device(const std::string& device_id) {
    const std::string path =
        std::string(kBusPath) + "/" + device_id + "/w1_slave";

    const std::string raw = read_file(path);
    if (raw.empty()) {
        log_error("DS18B20: unable to read " + path);
        return SensorData::empty("ds18b20", "read failed");
    }

    // --- CRC check (first line must end with "YES") ------------------
    if (raw.find("YES") == std::string::npos) {
        log_warning("DS18B20: CRC check failed for " + device_id);
        return SensorData::empty("ds18b20", "CRC failed");
    }

    // --- Extract temperature -----------------------------------------
    const auto pos = raw.find("t=");
    if (pos == std::string::npos) {
        log_error("DS18B20: 't=' token not found in " + path);
        return SensorData::empty("ds18b20", "parse error");
    }

    const double temp_c =
        std::stod(raw.substr(pos + 2)) / 1000.0;

    // --- Range validation --------------------------------------------
    if (temp_c < kMinValid || temp_c > kMaxValid) {
        log_warning("DS18B20: value " + std::to_string(temp_c) +
                    " °C is out of sensor range");
        return SensorData::empty("ds18b20", "out of range");
    }

    log_info("DS18B20 [" + device_id + "]: " +
             std::to_string(temp_c) + " °C");

    return SensorData{
        "ds18b20",
        "DS18B20 (" + device_id + ")",
        temp_c,
        "°C",
        now_ms(),
        true,
        0.0,
        ""};
}

} // namespace echosmart
