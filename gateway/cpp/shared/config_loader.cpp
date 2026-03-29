/**
 * @file config_loader.cpp
 * @brief Implementation of .env and sensors.json parsing.
 */

#include "config_loader.h"
#include "file_utils.h"

#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>

namespace echosmart {

// =======================================================================
// GatewayConfig — .env loader
// =======================================================================

/// Safe string-to-int with a fallback for malformed input.
static int safe_stoi(const std::string& s, int fallback) {
    try {
        return std::stoi(s);
    } catch (...) {
        return fallback;
    }
}

static bool is_truthy(const std::string& val) {
    return val == "true" || val == "1" || val == "yes";
}

static void apply_config_key(GatewayConfig& cfg,
                             const std::string& key,
                             const std::string& val) {
    if      (key == "GATEWAY_ID")        cfg.gateway_id       = val;
    else if (key == "GATEWAY_NAME")      cfg.gateway_name     = val;
    else if (key == "CLOUD_API_URL")     cfg.cloud_api_url    = val;
    else if (key == "CLOUD_API_KEY")     cfg.cloud_api_key    = val;
    else if (key == "MQTT_BROKER")       cfg.mqtt_broker      = val;
    else if (key == "MQTT_PORT")         cfg.mqtt_port        = safe_stoi(val, cfg.mqtt_port);
    else if (key == "POLLING_INTERVAL")  cfg.polling_interval = safe_stoi(val, cfg.polling_interval);
    else if (key == "SYNC_INTERVAL")     cfg.sync_interval    = safe_stoi(val, cfg.sync_interval);
    else if (key == "SIMULATION_MODE")   cfg.simulation_mode  = is_truthy(val);
    else if (key == "LOG_LEVEL")         cfg.log_level        = val;
    // Unknown keys are silently ignored — forward compatibility.
}

GatewayConfig GatewayConfig::load(const std::string& env_path) {
    GatewayConfig cfg;

    std::ifstream file(env_path);
    if (!file.is_open()) return cfg;  // all defaults

    std::string line;
    while (std::getline(file, line)) {
        line = trim(line);

        // Skip empty lines and comments.
        if (line.empty() || line[0] == '#') continue;

        auto eq_pos = line.find('=');
        if (eq_pos == std::string::npos) continue;

        std::string key = trim(line.substr(0, eq_pos));
        std::string val = trim(line.substr(eq_pos + 1));

        if (key.empty()) continue;

        apply_config_key(cfg, key, val);
    }

    return cfg;
}

// =======================================================================
// SensorEntry — sensors.json loader
// =======================================================================

/// Return the built-in sensor set (used when sensors.json is missing).
static std::vector<SensorEntry> default_sensor_list() {
    return {
        {"ds18b20",       "Temperatura Zona A", "28-xxxxxxxxxxxx", -1, "",     -1, ""},
        {"dht22",         "Temp + Humedad Zona A", "",              4, "",     -1, ""},
        {"bh1750",        "Luminosidad Zona A",    "",             -1, "0x23", -1, ""},
        {"soil_moisture", "Humedad Suelo Zona A",  "",             -1, "",      0, ""},
        {"mhz19c",        "CO2 Zona A",            "",             -1, "",     -1, "/dev/ttyS0"},
    };
}

// -----------------------------------------------------------------------
// Minimal JSON string-value extractor (avoids external dependency)
// -----------------------------------------------------------------------

/// Find the string value for @p key inside a JSON object fragment.
/// Looks for  "key":"value"  and returns value (unescaped).
static std::string json_extract_string(const std::string& obj,
                                       const std::string& key) {
    const std::string needle = "\"" + key + "\"";
    auto kpos = obj.find(needle);
    if (kpos == std::string::npos) return "";

    // Find the colon after the key.
    auto colon = obj.find(':', kpos + needle.size());
    if (colon == std::string::npos) return "";

    // Skip whitespace after the colon.
    auto start = colon + 1;
    while (start < obj.size() && (obj[start] == ' ' || obj[start] == '\t')) ++start;

    if (start >= obj.size() || obj[start] != '"') return "";

    ++start;  // skip opening quote
    std::string result;
    for (auto i = start; i < obj.size(); ++i) {
        if (obj[i] == '\\' && i + 1 < obj.size()) {
            result += obj[++i];
        } else if (obj[i] == '"') {
            break;
        } else {
            result += obj[i];
        }
    }
    return result;
}

/// Find a numeric value for @p key inside a JSON object fragment.
/// Returns @p fallback if the key is absent or not a number.
static int json_extract_int(const std::string& obj,
                            const std::string& key,
                            int fallback = -1) {
    const std::string needle = "\"" + key + "\"";
    auto kpos = obj.find(needle);
    if (kpos == std::string::npos) return fallback;

    auto colon = obj.find(':', kpos + needle.size());
    if (colon == std::string::npos) return fallback;

    auto start = colon + 1;
    while (start < obj.size() && (obj[start] == ' ' || obj[start] == '\t')) ++start;

    // May be a quoted integer like "4" or a bare integer like 4.
    if (start < obj.size() && obj[start] == '"') {
        std::string inner = json_extract_string(obj, key);
        return safe_stoi(inner, fallback);
    }

    char* end_ptr = nullptr;
    long val = std::strtol(obj.c_str() + start, &end_ptr, 10);
    if (end_ptr == obj.c_str() + start) return fallback;
    return static_cast<int>(val);
}

/// Parse a single sensor entry from a JSON object substring.
static SensorEntry parse_sensor_object(const std::string& obj) {
    SensorEntry entry;
    entry.type      = json_extract_string(obj, "type");
    entry.name      = json_extract_string(obj, "name");
    entry.device_id = json_extract_string(obj, "device_id");
    entry.pin       = json_extract_int(obj, "pin");
    entry.address   = json_extract_string(obj, "address");
    entry.channel   = json_extract_int(obj, "channel");
    entry.port      = json_extract_string(obj, "port");
    return entry;
}

/// Split the JSON content into individual object blocks by matching braces.
/// Each returned string is the text between (and including) { and }.
static std::vector<std::string> split_json_objects(const std::string& json) {
    std::vector<std::string> objects;
    int depth = 0;
    size_t start = 0;

    // We look for objects inside the top-level "sensors" array.
    // Find the opening '[' of the sensors array.
    auto arr_start = json.find('[');
    if (arr_start == std::string::npos) return objects;

    for (size_t i = arr_start; i < json.size(); ++i) {
        if (json[i] == '{') {
            if (depth == 0) start = i;
            ++depth;
        } else if (json[i] == '}') {
            --depth;
            if (depth == 0) {
                objects.push_back(json.substr(start, i - start + 1));
            }
        }
    }

    return objects;
}

std::vector<SensorEntry> SensorEntry::load_sensors(const std::string& json_path) {
    std::string content = read_file(json_path);
    if (content.empty()) return default_sensor_list();

    auto object_blocks = split_json_objects(content);
    if (object_blocks.empty()) return default_sensor_list();

    std::vector<SensorEntry> entries;
    entries.reserve(object_blocks.size());

    for (const auto& block : object_blocks) {
        SensorEntry entry = parse_sensor_object(block);
        if (!entry.type.empty()) {
            entries.push_back(std::move(entry));
        }
    }

    return entries.empty() ? default_sensor_list() : entries;
}

} // namespace echosmart
