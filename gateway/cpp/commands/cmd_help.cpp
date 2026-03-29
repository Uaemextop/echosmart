/**
 * @file cmd_help.cpp
 * @brief Implementation of the "help" command — usage information.
 */

#include "cmd_help.h"

#include "../shared/version.h"

#include <iostream>
#include <map>
#include <string>

namespace echosmart {

// -----------------------------------------------------------------------
// Per-command detailed help
// -----------------------------------------------------------------------

static const std::map<std::string, std::string>& command_help() {
    static const std::map<std::string, std::string> help = {
        {"read",
            "echosmart read <sensor_type> [--simulate]\n\n"
            "Read a single sensor and print the result as JSON.\n\n"
            "Arguments:\n"
            "  sensor_type   Sensor driver to use (ds18b20, dht22, bh1750,\n"
            "                soil_moisture, mhz19c)\n\n"
            "Options:\n"
            "  --simulate    Use simulated data (default: true)\n"},

        {"sysinfo",
            "echosmart sysinfo [--format=json|text]\n\n"
            "Print system diagnostics: hostname, CPU temperature, memory,\n"
            "disk usage, load average, and uptime.\n\n"
            "Options:\n"
            "  --format      Output format: json (default) or text\n"},

        {"run",
            "echosmart run [options]\n\n"
            "Start the gateway daemon polling loop.\n\n"
            "Options:\n"
            "  --config=PATH     Path to gateway.env      (default: /etc/echosmart/gateway.env)\n"
            "  --sensors=PATH    Path to sensors.json     (default: /etc/echosmart/sensors.json)\n"
            "  --simulate        Force simulation mode\n"
            "  --once            Run a single poll cycle and exit\n"
            "  --interval=SEC    Override polling interval\n"},

        {"setup",
            "echosmart setup [--config=PATH]\n\n"
            "Interactive wizard to configure the gateway.\n"
            "Prompts for gateway ID, name, API URL, API key,\n"
            "MQTT broker, and polling interval.\n\n"
            "Options:\n"
            "  --config=PATH   Where to write the config file\n"
            "                  (default: /etc/echosmart/gateway.env)\n"},

        {"status",
            "echosmart status [--format=json|text] [--config=PATH] [--sensors=PATH]\n\n"
            "Print the current gateway status including configuration,\n"
            "configured sensors, and a simulated reading cycle.\n\n"
            "Options:\n"
            "  --format          Output format: json (default) or text\n"
            "  --config=PATH     Path to gateway.env\n"
            "  --sensors=PATH    Path to sensors.json\n"},

        {"calibrate",
            "echosmart calibrate <sensor_type> --dry=<value> --wet=<value>\n\n"
            "Calibrate a sensor. Currently supports soil moisture only.\n\n"
            "Arguments:\n"
            "  sensor_type    Sensor to calibrate (soil)\n\n"
            "Options:\n"
            "  --dry=VALUE    Raw ADC reading in dry conditions (0% moisture)\n"
            "  --wet=VALUE    Raw ADC reading in wet conditions (100% moisture)\n"},

        {"list",
            "echosmart list [--format=json|text] [--sensors=PATH]\n\n"
            "List all configured sensors from the sensors.json file.\n\n"
            "Options:\n"
            "  --format          Output format: json (default) or text\n"
            "  --sensors=PATH    Path to sensors.json\n"},

        {"test",
            "echosmart test [sensor_type|all]\n\n"
            "Test sensor drivers in simulation mode.\n"
            "If no sensor type is given, tests all supported drivers.\n\n"
            "Arguments:\n"
            "  sensor_type    Specific sensor to test, or 'all' (default)\n"},

        {"version",
            "echosmart version\n\n"
            "Print the gateway version and exit.\n"},

        {"help",
            "echosmart help [command]\n\n"
            "Show general help or detailed help for a specific command.\n"},
    };
    return help;
}

// -----------------------------------------------------------------------
// General help
// -----------------------------------------------------------------------

static void print_general_help() {
    std::cout << "EchoSmart Gateway v" << es_version() << "\n\n"
              << "Usage: echosmart <command> [input] [options]\n\n"
              << "Commands:\n"
              << "  read        Read a sensor and print JSON\n"
              << "  sysinfo     Print system diagnostics\n"
              << "  run         Start the gateway daemon\n"
              << "  setup       Interactive configuration wizard\n"
              << "  status      Print gateway status\n"
              << "  calibrate   Calibrate a sensor\n"
              << "  list        List configured sensors\n"
              << "  test        Test sensor drivers\n"
              << "  version     Print version\n"
              << "  help        Show this help\n\n"
              << "Run 'echosmart help <command>' for detailed help.\n";
}

// -----------------------------------------------------------------------
// Command entry point
// -----------------------------------------------------------------------

int cmd_help(const CliArgs& args) {
    if (args.input.empty()) {
        print_general_help();
        return 0;
    }

    const auto& help = command_help();
    auto it = help.find(args.input);
    if (it != help.end()) {
        std::cout << it->second << "\n";
        return 0;
    }

    std::cerr << "Unknown command: " << args.input << "\n\n";
    print_general_help();
    return 1;
}

} // namespace echosmart
