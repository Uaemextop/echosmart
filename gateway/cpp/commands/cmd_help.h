/**
 * @file cmd_help.h
 * @brief "help" command — print usage information.
 */

#pragma once

#include "../cli.h"

namespace echosmart {

/// Print general help (all commands) or detailed help for a specific command.
int cmd_help(const CliArgs& args);

} // namespace echosmart
