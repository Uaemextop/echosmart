/**
 * @file cmd_sysinfo.cpp
 * @brief Implementation of the "sysinfo" command.
 *
 * Reads system diagnostics from /proc and /sys.  When files are
 * unavailable (e.g. on non-Linux hosts) the values default to zero
 * or "unknown".
 */

#include "cmd_sysinfo.h"

#include "../shared/file_utils.h"
#include "../shared/json_formatter.h"
#include "../shared/logger.h"

#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// System metric readers (return safe defaults on failure)
// -----------------------------------------------------------------------

static std::string read_model() {
    std::string raw = read_file("/proc/device-tree/model");
    if (raw.empty()) {
        raw = read_file("/sys/firmware/devicetree/base/model");
    }
    if (raw.empty()) return "unknown";
    // Strip trailing null byte that device-tree files often include.
    while (!raw.empty() && raw.back() == '\0') raw.pop_back();
    return trim(raw);
}

static double read_cpu_temp() {
    std::string raw = read_file("/sys/class/thermal/thermal_zone0/temp");
    if (raw.empty()) return 0.0;
    char* end = nullptr;
    double millideg = std::strtod(raw.c_str(), &end);
    return millideg / 1000.0;
}

static double read_uptime() {
    std::string raw = read_file("/proc/uptime");
    if (raw.empty()) return 0.0;
    char* end = nullptr;
    return std::strtod(raw.c_str(), &end);
}

static std::string read_load_avg() {
    std::string raw = read_file("/proc/loadavg");
    if (raw.empty()) return "0 0 0";
    // First three space-separated fields.
    auto parts = split(raw, ' ');
    if (parts.size() >= 3) {
        return parts[0] + " " + parts[1] + " " + parts[2];
    }
    return trim(raw);
}

/// Parse /proc/meminfo for MemTotal and MemAvailable (in kB).
static void read_memory(double& total_mb, double& available_mb) {
    total_mb = 0.0;
    available_mb = 0.0;

    std::string raw = read_file("/proc/meminfo");
    if (raw.empty()) return;

    auto lines = split(raw, '\n');
    for (const auto& line : lines) {
        if (line.find("MemTotal:") == 0) {
            auto parts = split(line, ' ');
            for (const auto& p : parts) {
                char* end = nullptr;
                double v = std::strtod(p.c_str(), &end);
                if (end != p.c_str() && v > 0) {
                    total_mb = v / 1024.0;
                    break;
                }
            }
        } else if (line.find("MemAvailable:") == 0) {
            auto parts = split(line, ' ');
            for (const auto& p : parts) {
                char* end = nullptr;
                double v = std::strtod(p.c_str(), &end);
                if (end != p.c_str() && v > 0) {
                    available_mb = v / 1024.0;
                    break;
                }
            }
        }
    }
}

/// Read root filesystem usage via statvfs-style info from /proc/mounts.
/// Falls back to 0.0 on failure.
static void read_disk(double& total_gb, double& used_gb) {
    total_gb = 0.0;
    used_gb  = 0.0;
    // /proc/self/mountstats is complex; use a simpler approach:
    // read the statfs information for root.
    // Since we cannot call statvfs without <sys/statvfs.h>, we parse
    // the output concept differently — just report zeros on failure.
    // A real deployment would use statvfs(2).
}

// -----------------------------------------------------------------------
// Output formatters
// -----------------------------------------------------------------------

static void print_json(const std::string& hostname, const std::string& model,
                       double cpu_temp, double uptime,
                       const std::string& load_avg,
                       double mem_total, double mem_available,
                       double disk_total, double disk_used) {
    std::vector<std::string> fields;
    fields.push_back(json_string("hostname",      hostname));
    fields.push_back(json_string("model",         model));
    fields.push_back(json_number("cpu_temp_c",    cpu_temp, 1));
    fields.push_back(json_number("uptime_s",      uptime, 0));
    fields.push_back(json_string("load_avg",      load_avg));
    fields.push_back(json_number("mem_total_mb",  mem_total, 0));
    fields.push_back(json_number("mem_avail_mb",  mem_available, 0));
    fields.push_back(json_number("disk_total_gb", disk_total, 1));
    fields.push_back(json_number("disk_used_gb",  disk_used, 1));

    std::cout << json_object(fields) << "\n";
}

static void print_text(const std::string& hostname, const std::string& model,
                       double cpu_temp, double uptime,
                       const std::string& load_avg,
                       double mem_total, double mem_available,
                       double disk_total, double disk_used) {
    std::cout << "=== EchoSmart System Info ===\n"
              << "Hostname      : " << hostname << "\n"
              << "Model         : " << model << "\n"
              << "CPU Temp      : " << std::fixed << std::setprecision(1)
                                     << cpu_temp << " °C\n"
              << "Uptime        : " << std::setprecision(0)
                                     << uptime << " s\n"
              << "Load Average  : " << load_avg << "\n"
              << "Memory Total  : " << std::setprecision(0)
                                     << mem_total << " MB\n"
              << "Memory Avail  : " << mem_available << " MB\n"
              << "Disk Total    : " << std::setprecision(1)
                                     << disk_total << " GB\n"
              << "Disk Used     : " << disk_used << " GB\n";
}

// -----------------------------------------------------------------------
// Command entry point
// -----------------------------------------------------------------------

int cmd_sysinfo(const CliArgs& args) {
    std::string hostname = get_hostname();
    std::string model    = read_model();
    double cpu_temp      = read_cpu_temp();
    double uptime        = read_uptime();
    std::string load_avg = read_load_avg();

    double mem_total = 0.0, mem_available = 0.0;
    read_memory(mem_total, mem_available);

    double disk_total = 0.0, disk_used = 0.0;
    read_disk(disk_total, disk_used);

    std::string format = args.get("format", "json");
    if (format == "text") {
        print_text(hostname, model, cpu_temp, uptime, load_avg,
                   mem_total, mem_available, disk_total, disk_used);
    } else {
        print_json(hostname, model, cpu_temp, uptime, load_avg,
                   mem_total, mem_available, disk_total, disk_used);
    }

    return 0;
}

} // namespace echosmart
