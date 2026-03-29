/**
 * @file main.cpp
 * @brief Entry point for the unified EchoSmart gateway CLI.
 *
 * Parses command-line arguments and dispatches to the appropriate
 * command handler.  Each command is a self-contained function that
 * returns an exit code.
 *
 * Usage:  echosmart <command> [input] [--key=value ...]
 */

#include "cli.h"

#include "commands/cmd_calibrate.h"
#include "commands/cmd_help.h"
#include "commands/cmd_list.h"
#include "commands/cmd_read.h"
#include "commands/cmd_run.h"
#include "commands/cmd_setup.h"
#include "commands/cmd_status.h"
#include "commands/cmd_sysinfo.h"
#include "commands/cmd_test.h"
#include "commands/cmd_version.h"

#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    echosmart::CliArgs args = echosmart::parse_args(argc, argv);

    // No command → print help.
    if (args.command.empty()) {
        return echosmart::cmd_help(args);
    }

    const std::string& cmd = args.command;

    if (cmd == "read")      return echosmart::cmd_read(args);
    if (cmd == "sysinfo")   return echosmart::cmd_sysinfo(args);
    if (cmd == "run")       return echosmart::cmd_run(args);
    if (cmd == "setup")     return echosmart::cmd_setup(args);
    if (cmd == "status")    return echosmart::cmd_status(args);
    if (cmd == "calibrate") return echosmart::cmd_calibrate(args);
    if (cmd == "list")      return echosmart::cmd_list(args);
    if (cmd == "test")      return echosmart::cmd_test(args);
    if (cmd == "version")   return echosmart::cmd_version(args);
    if (cmd == "help")      return echosmart::cmd_help(args);

    // Unknown command.
    std::cerr << "Unknown command: " << cmd << "\n\n";
    return echosmart::cmd_help(args);
}
