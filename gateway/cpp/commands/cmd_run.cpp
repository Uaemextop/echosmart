/**
 * @file cmd_run.cpp
 * @brief Implementation of the "run" command — gateway daemon entry point.
 */

#include "cmd_run.h"

#include "../core/gateway.h"
#include "../shared/config_loader.h"
#include "../shared/logger.h"

#include <csignal>
#include <chrono>
#include <iostream>
#include <string>
#include <thread>

namespace echosmart {

// -----------------------------------------------------------------------
// Signal handling
// -----------------------------------------------------------------------

static volatile sig_atomic_t g_running = 1;

static void signal_handler(int /*sig*/) {
    g_running = 0;
}

static void install_signal_handlers() {
    std::signal(SIGINT,  signal_handler);
    std::signal(SIGTERM, signal_handler);
}

// -----------------------------------------------------------------------
// Command entry point
// -----------------------------------------------------------------------

int cmd_run(const CliArgs& args) {
    // Resolve configuration paths.
    std::string config_path  = args.get("config",  "/etc/echosmart/gateway.env");
    std::string sensors_path = args.get("sensors", "/etc/echosmart/sensors.json");

    // Load configuration.
    GatewayConfig config = GatewayConfig::load(config_path);

    // Apply CLI overrides.
    bool simulate = args.get_bool("simulate", config.simulation_mode);
    config.simulation_mode = simulate;

    int interval = args.get_int("interval", config.polling_interval);
    config.polling_interval = interval;

    // Configure logging.
    set_log_level(parse_log_level(config.log_level));

    // Load sensor inventory.
    std::vector<SensorEntry> sensors = SensorEntry::load_sensors(sensors_path);

    log_info("EchoSmart gateway starting");
    log_info("  config  : " + config_path);
    log_info("  sensors : " + sensors_path);
    log_info("  mode    : " + std::string(simulate ? "simulation" : "hardware"));
    log_info("  interval: " + std::to_string(config.polling_interval) + "s");
    log_info("  sensors : " + std::to_string(sensors.size()) + " configured");

    // Create the gateway.
    Gateway gateway(config, sensors, simulate);

    // Single-cycle mode.
    if (args.get_bool("once", false)) {
        log_info("Running single poll cycle (--once)");
        gateway.run_once();
        log_info("Single cycle complete");
        return 0;
    }

    // Continuous mode with signal handling.
    install_signal_handlers();
    log_info("Entering polling loop (Ctrl+C to stop)");

    // Poll loop — delegate to Gateway but check g_running flag.
    while (g_running) {
        gateway.run_once();

        // Sleep in 1-second increments so we can respond to signals.
        for (int i = 0; i < config.polling_interval && g_running; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    gateway.shutdown();
    log_info("EchoSmart gateway stopped (polls: "
             + std::to_string(gateway.poll_count()) + ")");

    return 0;
}

} // namespace echosmart
