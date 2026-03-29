/**
 * @file cmd_sysinfo.h
 * @brief "sysinfo" command — print system diagnostics.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Collect and print system information (hostname, CPU temp, memory, etc.).
/// Supports --format=json|text (default: json).
int cmd_sysinfo(const CliArgs& args);

} // namespace echosmart
