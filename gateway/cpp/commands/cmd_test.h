/**
 * @file cmd_test.h
 * @brief "test" command — test one or all sensors.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Test a specific sensor type or all supported sensors.
/// Prints PASS/FAIL for each and returns the count of failures.
int cmd_test(const CliArgs& args);

} // namespace echosmart
