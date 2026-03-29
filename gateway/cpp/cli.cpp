/**
 * @file cli.cpp
 * @brief Implementation of the EchoSmart CLI argument parser.
 */

#include "cli.h"

#include <cstdlib>
#include <limits>

namespace echosmart {

// -----------------------------------------------------------------------
// CliArgs accessors
// -----------------------------------------------------------------------

bool CliArgs::has(const std::string& key) const {
    return options.find(key) != options.end();
}

std::string CliArgs::get(const std::string& key,
                         const std::string& default_val) const {
    auto it = options.find(key);
    return (it != options.end()) ? it->second : default_val;
}

bool CliArgs::get_bool(const std::string& key, bool default_val) const {
    auto it = options.find(key);
    if (it == options.end()) return default_val;

    const std::string& v = it->second;
    return (v == "true" || v == "1" || v == "yes");
}

int CliArgs::get_int(const std::string& key, int default_val) const {
    auto it = options.find(key);
    if (it == options.end()) return default_val;

    char* end = nullptr;
    long val = std::strtol(it->second.c_str(), &end, 10);
    if (end == it->second.c_str()) return default_val;

    // Guard against long → int truncation.
    if (val > std::numeric_limits<int>::max()) return std::numeric_limits<int>::max();
    if (val < std::numeric_limits<int>::min()) return std::numeric_limits<int>::min();

    return static_cast<int>(val);
}

// -----------------------------------------------------------------------
// Argument parsing
// -----------------------------------------------------------------------

/// Strip the leading dashes from an option token (e.g. "--key" → "key").
static std::string strip_dashes(const std::string& arg) {
    std::string::size_type start = 0;
    while (start < arg.size() && arg[start] == '-') ++start;
    return arg.substr(start);
}

CliArgs parse_args(int argc, char* argv[]) {
    CliArgs args;

    if (argc < 2) return args;

    // First non-option argument is the command.
    args.command = argv[1];

    for (int i = 2; i < argc; ++i) {
        std::string token = argv[i];

        if (token.size() >= 2 && token[0] == '-' && token[1] == '-') {
            // Option token: --key=value  or  --key value  or  --flag
            auto eq_pos = token.find('=');

            if (eq_pos != std::string::npos) {
                // --key=value
                std::string key   = strip_dashes(token.substr(0, eq_pos));
                std::string value = token.substr(eq_pos + 1);
                args.options[key] = value;
            } else {
                std::string key = strip_dashes(token);

                // Peek at the next token: if it exists and is not an option,
                // treat it as the value for this key.
                if (i + 1 < argc) {
                    std::string next = argv[i + 1];
                    if (next.size() >= 2 && next[0] == '-' && next[1] == '-') {
                        // Next token is another option → current is a flag.
                        args.options[key] = "true";
                    } else {
                        args.options[key] = next;
                        ++i;   // consume the value token
                    }
                } else {
                    // Last token → flag.
                    args.options[key] = "true";
                }
            }
        } else if (args.input.empty()) {
            // First positional argument after the command.
            args.input = token;
        }
    }

    return args;
}

} // namespace echosmart
