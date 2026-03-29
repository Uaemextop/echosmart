/**
 * @file cmd_status.h
 * @brief "status" command — print gateway status summary.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Print current gateway status: configuration, sensors, and a simulated
/// reading cycle.  Supports --format=json|text (default: json).
int cmd_status(const CliArgs& args);

} // namespace echosmart
