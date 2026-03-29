/**
 * @file sensor_data.cpp
 * @brief Implementation of SensorData serialisation and factory helpers.
 */

#include "sensor_data.h"
#include "json_formatter.h"

#include <chrono>
#include <cstdlib>
#include <string>

namespace echosmart {

// -----------------------------------------------------------------------
// Helpers — minimal JSON value extraction (no external parser)
// -----------------------------------------------------------------------

/// Find a JSON string value by key.  Returns "" if not found.
static std::string extract_json_string(const std::string& json,
                                       const std::string& key) {
    const std::string search = "\"" + key + "\":\"";
    auto pos = json.find(search);
    if (pos == std::string::npos) return "";

    auto start = pos + search.size();
    auto end   = json.find('"', start);
    if (end == std::string::npos) return "";

    return json.substr(start, end - start);
}

/// Find a JSON numeric value by key.  Returns @p fallback if not found.
static double extract_json_number(const std::string& json,
                                  const std::string& key,
                                  double fallback = 0.0) {
    const std::string search = "\"" + key + "\":";
    auto pos = json.find(search);
    if (pos == std::string::npos) return fallback;

    auto start = pos + search.size();
    // Skip whitespace after the colon.
    while (start < json.size() && json[start] == ' ') ++start;

    char* end_ptr = nullptr;
    double result = std::strtod(json.c_str() + start, &end_ptr);
    if (end_ptr == json.c_str() + start) return fallback;

    return result;
}

/// Find a JSON boolean value by key.  Returns @p fallback if not found.
static bool extract_json_bool(const std::string& json,
                              const std::string& key,
                              bool fallback = false) {
    const std::string search = "\"" + key + "\":";
    auto pos = json.find(search);
    if (pos == std::string::npos) return fallback;

    auto start = pos + search.size();
    while (start < json.size() && json[start] == ' ') ++start;

    if (json.compare(start, 4, "true") == 0) return true;
    if (json.compare(start, 5, "false") == 0) return false;

    return fallback;
}

// -----------------------------------------------------------------------
// Current epoch milliseconds
// -----------------------------------------------------------------------

static int64_t epoch_ms_now() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(
        system_clock::now().time_since_epoch()
    ).count();
}

// -----------------------------------------------------------------------
// Serialisation
// -----------------------------------------------------------------------

std::string SensorData::to_json() const {
    std::vector<std::string> fields;
    fields.reserve(8);

    fields.push_back(json_string("sensor_type", sensor_type));
    fields.push_back(json_string("sensor_name", sensor_name));
    fields.push_back(json_number("value",       value, 2));
    fields.push_back(json_string("unit",        unit));
    fields.push_back(json_int("timestamp_ms",   timestamp_ms));
    fields.push_back(json_bool("is_valid",      is_valid));

    const bool has_secondary = !secondary_unit.empty();
    if (has_secondary) {
        fields.push_back(json_number("secondary_value", secondary_value, 2));
        fields.push_back(json_string("secondary_unit",  secondary_unit));
    }

    return json_object(fields);
}

SensorData SensorData::from_json(const std::string& json) {
    SensorData sd;

    sd.sensor_type     = extract_json_string(json, "sensor_type");
    sd.sensor_name     = extract_json_string(json, "sensor_name");
    sd.value           = extract_json_number(json, "value");
    sd.unit            = extract_json_string(json, "unit");
    sd.timestamp_ms    = static_cast<int64_t>(extract_json_number(json, "timestamp_ms"));
    sd.is_valid        = extract_json_bool(json,   "is_valid");
    sd.secondary_value = extract_json_number(json, "secondary_value");
    sd.secondary_unit  = extract_json_string(json, "secondary_unit");

    return sd;
}

// -----------------------------------------------------------------------
// Factory helpers
// -----------------------------------------------------------------------

SensorData SensorData::empty(const std::string& type,
                             const std::string& error_msg) {
    SensorData sd;
    sd.sensor_type  = type;
    sd.sensor_name  = error_msg;
    sd.value        = 0.0;
    sd.unit         = "";
    sd.timestamp_ms = epoch_ms_now();
    sd.is_valid     = false;
    return sd;
}

} // namespace echosmart
