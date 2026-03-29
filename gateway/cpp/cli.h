/**
 * @file cli.h
 * @brief Command-line argument parser for the EchoSmart gateway CLI.
 *
 * Parses the canonical syntax:
 *     echosmart <command> [input] [--key=value ...] [--flag]
 *
 * The parser is a pure function with no side effects — it only transforms
 * the raw argc/argv into a typed CliArgs struct.
 */

#pragma once

#include <map>
#include <string>
#include <vector>

namespace echosmart {

struct CliArgs {
    std::string command;                          ///< e.g. "read", "run", "sysinfo"
    std::string input;                            ///< positional argument after command
    std::map<std::string, std::string> options;   ///< --key=value or --flag pairs

    /// Check whether an option key exists.
    bool has(const std::string& key) const;

    /// Retrieve an option value, returning @p default_val when absent.
    std::string get(const std::string& key, const std::string& default_val = "") const;

    /// Retrieve a boolean option ("true"/"1" → true).
    bool get_bool(const std::string& key, bool default_val = false) const;

    /// Retrieve an integer option, returning @p default_val on parse failure.
    int get_int(const std::string& key, int default_val = 0) const;
};

/// Parse raw command-line arguments into a CliArgs struct.
CliArgs parse_args(int argc, char* argv[]);

} // namespace echosmart
