/**
 * @file cmd_run.h
 * @brief "run" command — start the gateway daemon polling loop.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Launch the gateway daemon. Loads configuration, creates the Gateway
/// instance, and enters the polling loop until SIGINT/SIGTERM.
/// Options: --simulate, --once, --interval, --config, --sensors.
int cmd_run(const CliArgs& args);

} // namespace echosmart
