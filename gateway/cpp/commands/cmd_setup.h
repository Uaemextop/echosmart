/**
 * @file cmd_setup.h
 * @brief "setup" command — interactive configuration wizard.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Interactive wizard that prompts for gateway settings and writes
/// them to a .env configuration file.
int cmd_setup(const CliArgs& args);

} // namespace echosmart
