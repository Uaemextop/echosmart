/**
 * echosmart-gateway — Main gateway daemon for the EchoSmart IoT kit.
 *
 * Orchestrates sensor polling, alert evaluation, JSON logging and
 * optional MQTT/HTTP data forwarding.  Designed to run as a systemd
 * service on Raspberry Pi OS (arm64).
 *
 * Usage:
 *   echosmart-gateway [OPTIONS]
 *
 * Options:
 *   --config <path>   Path to gateway.env config   (default /etc/echosmart/gateway.env)
 *   --sensors <path>  Path to sensors.json          (default /etc/echosmart/sensors.json)
 *   --simulate        Use simulated sensor readings (no hardware required)
 *   --once            Poll once and exit
 *   --interval <sec>  Polling interval in seconds   (default 60)
 *   --version         Print version and exit
 *   --help            Show usage
 *
 * Build:  cmake gateway/cpp && make
 */

#include <chrono>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#ifndef VERSION
#define VERSION "1.0.0"
#endif

// ---------------------------------------------------------------------------
// Global state
// ---------------------------------------------------------------------------

static volatile bool g_running = true;

static void signal_handler(int) { g_running = false; }

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

static std::string trim(const std::string &s) {
    auto b = s.find_first_not_of(" \t\n\r");
    if (b == std::string::npos) return "";
    auto e = s.find_last_not_of(" \t\n\r");
    return s.substr(b, e - b + 1);
}

static std::string now_iso() {
    auto t  = std::time(nullptr);
    auto tm = *std::localtime(&t);
    char buf[32];
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S", &tm);
    return std::string(buf);
}

static void log_info(const std::string &msg) {
    std::cout << now_iso() << " [INFO]  " << msg << "\n";
}

static void log_error(const std::string &msg) {
    std::cerr << now_iso() << " [ERROR] " << msg << "\n";
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

struct GatewayConfig {
    std::string gateway_id    = "gw-001";
    std::string gateway_name  = "EchoSmart Gateway";
    std::string cloud_api_url = "http://localhost:8000";
    std::string cloud_api_key;
    std::string mqtt_broker   = "localhost";
    int         mqtt_port     = 1883;
    int         polling_interval = 60;
    int         sync_interval = 300;
    bool        simulation    = false;
    std::string log_level     = "INFO";
};

static GatewayConfig load_config(const std::string &path) {
    GatewayConfig cfg;
    std::ifstream f(path);
    if (!f.is_open()) return cfg;
    std::string line;
    while (std::getline(f, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') continue;
        auto eq = line.find('=');
        if (eq == std::string::npos) continue;
        auto key = trim(line.substr(0, eq));
        auto val = trim(line.substr(eq + 1));
        if (key == "GATEWAY_ID")        cfg.gateway_id = val;
        else if (key == "GATEWAY_NAME") cfg.gateway_name = val;
        else if (key == "CLOUD_API_URL") cfg.cloud_api_url = val;
        else if (key == "CLOUD_API_KEY") cfg.cloud_api_key = val;
        else if (key == "MQTT_BROKER")   cfg.mqtt_broker = val;
        else if (key == "MQTT_PORT")     cfg.mqtt_port = std::stoi(val);
        else if (key == "POLLING_INTERVAL") cfg.polling_interval = std::stoi(val);
        else if (key == "SYNC_INTERVAL") cfg.sync_interval = std::stoi(val);
        else if (key == "SIMULATION_MODE") cfg.simulation = (val == "true" || val == "1");
        else if (key == "LOG_LEVEL")     cfg.log_level = val;
    }
    return cfg;
}

// ---------------------------------------------------------------------------
// Sensor list from sensors.json (minimal JSON parser — no dependencies)
// ---------------------------------------------------------------------------

struct SensorEntry {
    std::string type;
    std::string name;
};

static std::vector<SensorEntry> load_sensors(const std::string &path) {
    std::vector<SensorEntry> list;
    std::ifstream f(path);
    if (!f.is_open()) {
        // Default sensor set
        list.push_back({"ds18b20", "Temperature"});
        list.push_back({"dht22",   "Temp+Humidity"});
        list.push_back({"bh1750",  "Light"});
        list.push_back({"soil",    "Soil Moisture"});
        list.push_back({"mhz19c",  "CO2"});
        return list;
    }
    // Simple line-by-line parse looking for "type" keys
    std::string content((std::istreambuf_iterator<char>(f)),
                         std::istreambuf_iterator<char>());
    // Very small JSON scanner for arrays of {"type":"...","name":"..."}
    size_t pos = 0;
    while ((pos = content.find("\"type\"", pos)) != std::string::npos) {
        auto colon = content.find(':', pos);
        auto q1 = content.find('"', colon + 1);
        auto q2 = content.find('"', q1 + 1);
        if (q1 == std::string::npos || q2 == std::string::npos) break;
        std::string type_val = content.substr(q1 + 1, q2 - q1 - 1);

        // find "name"
        std::string name_val = type_val;
        auto np = content.find("\"name\"", q2);
        if (np != std::string::npos && np < content.find('}', q2)) {
            auto nc = content.find(':', np);
            auto nq1 = content.find('"', nc + 1);
            auto nq2 = content.find('"', nq1 + 1);
            if (nq1 != std::string::npos && nq2 != std::string::npos)
                name_val = content.substr(nq1 + 1, nq2 - nq1 - 1);
        }
        list.push_back({type_val, name_val});
        pos = q2 + 1;
    }
    return list;
}

// ---------------------------------------------------------------------------
// Poll sensors via the echosmart-sensor-read binary
// ---------------------------------------------------------------------------

static std::string poll_sensor(const std::string &type, bool simulate) {
    std::string cmd = "echosmart-sensor-read " + type;
    if (simulate) cmd += " --simulate";
    cmd += " 2>/dev/null";

    FILE *fp = popen(cmd.c_str(), "r");
    if (!fp) return "";
    char buf[1024];
    std::string output;
    while (fgets(buf, sizeof(buf), fp)) output += buf;
    pclose(fp);
    return trim(output);
}

// ---------------------------------------------------------------------------
// Simple alert evaluation (threshold check on JSON value field)
// ---------------------------------------------------------------------------

static double extract_value(const std::string &json) {
    // Look for "value": in the JSON string
    auto pos = json.find("\"value\":");
    if (pos == std::string::npos) return -9999.0;
    auto start = pos + 8;
    while (start < json.size() && (json[start] == ' ' || json[start] == '\t')) ++start;
    return std::strtod(json.c_str() + start, nullptr);
}

struct AlertRule {
    std::string sensor_type;
    std::string condition;  // "gt" or "lt"
    double threshold;
    std::string severity;
    std::string message;
};

static std::vector<AlertRule> default_alerts() {
    return {
        {"ds18b20", "gt", 40.0, "critical", "Temperature above 40°C"},
        {"ds18b20", "lt",  5.0, "warning",  "Temperature below 5°C"},
        {"mhz19c",  "gt", 2000.0, "critical", "CO2 above 2000 ppm"},
    };
}

static void check_alerts(const std::string &sensor_type,
                          double value,
                          const std::vector<AlertRule> &rules) {
    for (const auto &r : rules) {
        if (r.sensor_type != sensor_type) continue;
        bool fired = false;
        if (r.condition == "gt" && value > r.threshold) fired = true;
        if (r.condition == "lt" && value < r.threshold) fired = true;
        if (fired) {
            log_info("ALERT [" + r.severity + "] " + r.message +
                     " (value=" + std::to_string(value) + ")");
        }
    }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

static void usage() {
    std::cout <<
        "Usage: echosmart-gateway [OPTIONS]\n"
        "\n"
        "Options:\n"
        "  --config <path>    Config file  (default /etc/echosmart/gateway.env)\n"
        "  --sensors <path>   Sensors JSON (default /etc/echosmart/sensors.json)\n"
        "  --simulate         Simulated sensor readings\n"
        "  --once             Poll once and exit\n"
        "  --interval <sec>   Polling interval in seconds (default 60)\n"
        "  --version          Print version\n"
        "  --help             Show this message\n";
}

int main(int argc, char *argv[]) {
    std::string config_path  = "/etc/echosmart/gateway.env";
    std::string sensors_path = "/etc/echosmart/sensors.json";
    bool simulate  = false;
    bool once_mode = false;
    int  interval  = -1;  // -1 → use config value

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--config"   && i + 1 < argc) { config_path  = argv[++i]; continue; }
        if (a == "--sensors"  && i + 1 < argc) { sensors_path = argv[++i]; continue; }
        if (a == "--interval" && i + 1 < argc) { interval = std::atoi(argv[++i]); continue; }
        if (a == "--simulate" || a == "-s") { simulate  = true; continue; }
        if (a == "--once")                  { once_mode = true; continue; }
        if (a == "--version" || a == "-v") {
            std::cout << "echosmart-gateway " << VERSION << "\n";
            return 0;
        }
        if (a == "--help" || a == "-h") { usage(); return 0; }
        std::cerr << "unknown option: " << a << "\n";
        usage();
        return 1;
    }

    // Signals
    std::signal(SIGINT,  signal_handler);
    std::signal(SIGTERM, signal_handler);

    // Load config
    GatewayConfig cfg = load_config(config_path);
    if (simulate) cfg.simulation = true;
    if (interval > 0) cfg.polling_interval = interval;

    log_info("EchoSmart Gateway v" + std::string(VERSION));
    log_info("Gateway ID: " + cfg.gateway_id);
    log_info("Simulation: " + std::string(cfg.simulation ? "on" : "off"));
    log_info("Polling interval: " + std::to_string(cfg.polling_interval) + "s");

    // Load sensors
    auto sensors = load_sensors(sensors_path);
    log_info("Loaded " + std::to_string(sensors.size()) + " sensor(s)");

    auto alerts = default_alerts();

    // Main loop
    do {
        log_info("--- polling cycle start ---");
        for (const auto &s : sensors) {
            std::string json = poll_sensor(s.type, cfg.simulation);
            if (json.empty()) {
                log_error("No reading from " + s.name + " (" + s.type + ")");
                continue;
            }
            log_info("[" + s.name + "] " + json);
            double val = extract_value(json);
            if (val > -9998.0) check_alerts(s.type, val, alerts);
        }
        log_info("--- polling cycle end ---");

        if (once_mode) break;

        // Sleep in 1-second increments so we can react to SIGTERM quickly
        for (int i = 0; i < cfg.polling_interval && g_running; ++i)
            std::this_thread::sleep_for(std::chrono::seconds(1));

    } while (g_running);

    log_info("Gateway stopped.");
    return 0;
}
