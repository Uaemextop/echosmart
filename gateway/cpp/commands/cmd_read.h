/**
 * @file cmd_read.h
 * @brief "read" command — read a single sensor and print JSON.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Read a sensor by type and print the result as JSON.
/// @return 0 on success, 1 if the sensor type is unknown, 2 on read error.
int cmd_read(const CliArgs& args);

} // namespace echosmart
