/**
 * @file cmd_list.h
 * @brief "list" command — list configured sensors.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Load sensors.json and print the sensor inventory.
/// Supports --format=json|text (default: json).
int cmd_list(const CliArgs& args);

} // namespace echosmart
