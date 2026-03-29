/**
 * @file cmd_version.h
 * @brief "version" command — print the gateway version.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Print the gateway version string and return 0.
int cmd_version(const CliArgs& args);

} // namespace echosmart
