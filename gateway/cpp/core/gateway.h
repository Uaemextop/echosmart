/**
 * @file gateway.h
 * @brief Gateway — the main daemon that orchestrates polling, alerting, and storage.
 *
 * Gateway owns a SensorPoller, AlertEngine, and DataStore.  The run()
 * method enters a polling loop that is stopped by calling shutdown() or
 * by an external signal handler setting g_running to false.
 */

#pragma once

#include "../shared/config_loader.h"
#include "alert_engine.h"
#include "data_store.h"
#include "sensor_poller.h"

#include <atomic>
#include <string>
#include <vector>

namespace echosmart {

class Gateway {
public:
    /// Construct the gateway with its configuration and sensor inventory.
    Gateway(const GatewayConfig& config,
            const std::vector<SensorEntry>& sensors,
            bool simulate);

    /// Enter the polling loop.  Blocks until shutdown() is called.
    void run();

    /// Execute a single poll-evaluate-store cycle.
    void run_once();

    /// Request a graceful shutdown (safe to call from a signal handler).
    void shutdown();

    /// Number of completed polling cycles.
    int poll_count() const;

    /// True while the polling loop is active.
    bool is_running() const;

private:
    GatewayConfig              config_;
    std::vector<SensorEntry>   sensors_;
    bool                       simulate_;

    SensorPoller               poller_;
    AlertEngine                alert_engine_;
    DataStore                  data_store_;

    std::atomic<bool>          running_{false};
    int                        poll_count_{0};
};

} // namespace echosmart
