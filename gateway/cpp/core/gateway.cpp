/**
 * @file gateway.cpp
 * @brief Implementation of the Gateway daemon.
 */

#include "gateway.h"

#include "../shared/logger.h"

#include <ctime>
#include <string>
#include <thread>

namespace echosmart {

// -----------------------------------------------------------------------
// Construction
// -----------------------------------------------------------------------

Gateway::Gateway(const GatewayConfig& config,
                 const std::vector<SensorEntry>& sensors,
                 bool simulate)
    : config_(config)
    , sensors_(sensors)
    , simulate_(simulate)
    , data_store_(DataStore("/var/lib/echosmart")) {}

// -----------------------------------------------------------------------
// Polling loop
// -----------------------------------------------------------------------

void Gateway::run() {
    running_ = true;
    log_info("Gateway entering polling loop (interval="
             + std::to_string(config_.polling_interval) + "s)");

    while (running_) {
        run_once();

        // Sleep in 1-second increments for responsive shutdown.
        for (int i = 0; i < config_.polling_interval && running_; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    log_info("Gateway polling loop exited");
}

void Gateway::run_once() {
    log_debug("Starting poll cycle #" + std::to_string(poll_count_ + 1));

    // 1. Poll all sensors.
    auto readings = poller_.poll_all(sensors_, simulate_);

    // 2. Evaluate alerts and persist data.
    for (const auto& reading : readings) {
        data_store_.save(reading);

        auto triggered = alert_engine_.evaluate(reading);
        for (const auto& [rule, data] : triggered) {
            data_store_.save_alert(rule, data);
        }
    }

    ++poll_count_;
    log_info("Poll cycle #" + std::to_string(poll_count_)
             + " complete: " + std::to_string(readings.size()) + " readings, "
             + std::to_string(alert_engine_.triggered_count()) + " alerts total");
}

// -----------------------------------------------------------------------
// Lifecycle
// -----------------------------------------------------------------------

void Gateway::shutdown() {
    running_ = false;
}

int Gateway::poll_count() const {
    return poll_count_;
}

bool Gateway::is_running() const {
    return running_;
}

} // namespace echosmart
