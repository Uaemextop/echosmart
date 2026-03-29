/**
 * @file cmd_calibrate.h
 * @brief "calibrate" command — calibrate a sensor (soil moisture).
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Calibrate a sensor using --dry and --wet raw ADC values.
/// Currently supports only "soil".
int cmd_calibrate(const CliArgs& args);

} // namespace echosmart
