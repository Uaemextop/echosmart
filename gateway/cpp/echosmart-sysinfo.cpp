/**
 * echosmart-sysinfo — Lightweight system diagnostics for the EchoSmart gateway.
 *
 * Outputs JSON with CPU temperature, memory, disk, uptime and load-average.
 * Designed to run on Raspberry Pi OS (arm64) but works on any Linux host.
 *
 * Usage:  echosmart-sysinfo [--version] [--help]
 *
 * Build:  cmake gateway/cpp && make
 */

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

#ifndef VERSION
#define VERSION "1.0.0"
#endif

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

static std::string trim(const std::string &s) {
    auto begin = s.find_first_not_of(" \t\n\r");
    if (begin == std::string::npos) return "";
    auto end = s.find_last_not_of(" \t\n\r");
    return s.substr(begin, end - begin + 1);
}

static std::string read_file(const char *path) {
    std::ifstream f(path);
    if (!f.is_open()) return "";
    std::string content((std::istreambuf_iterator<char>(f)),
                         std::istreambuf_iterator<char>());
    return trim(content);
}

// ---------------------------------------------------------------------------
// Collectors
// ---------------------------------------------------------------------------

struct MemInfo {
    long total_kb = 0;
    long available_kb = 0;
};

static MemInfo get_memory() {
    MemInfo m;
    std::ifstream f("/proc/meminfo");
    if (!f.is_open()) return m;
    std::string line;
    while (std::getline(f, line)) {
        if (line.rfind("MemTotal:", 0) == 0)
            std::sscanf(line.c_str(), "MemTotal: %ld kB", &m.total_kb);
        else if (line.rfind("MemAvailable:", 0) == 0)
            std::sscanf(line.c_str(), "MemAvailable: %ld kB", &m.available_kb);
    }
    return m;
}

struct DiskInfo {
    unsigned long long total_bytes = 0;
    unsigned long long free_bytes = 0;
};

static DiskInfo get_disk(const char *path = "/") {
    DiskInfo d;
    FILE *fp = popen("df -B1 / 2>/dev/null | tail -1", "r");
    if (!fp) return d;
    char buf[512];
    if (fgets(buf, sizeof(buf), fp)) {
        char dev[128];
        unsigned long long total, used, avail;
        if (std::sscanf(buf, "%127s %llu %llu %llu", dev, &total, &used, &avail) == 4) {
            d.total_bytes = total;
            d.free_bytes = avail;
        }
    }
    pclose(fp);
    return d;
}

static double get_cpu_temp() {
    std::string raw = read_file("/sys/class/thermal/thermal_zone0/temp");
    if (raw.empty()) return -1.0;
    return std::stod(raw) / 1000.0;
}

static double get_uptime() {
    std::string raw = read_file("/proc/uptime");
    if (raw.empty()) return -1.0;
    return std::stod(raw.substr(0, raw.find(' ')));
}

struct LoadAvg {
    double one = 0, five = 0, fifteen = 0;
};

static LoadAvg get_load() {
    LoadAvg la;
    std::string raw = read_file("/proc/loadavg");
    if (raw.empty()) return la;
    std::sscanf(raw.c_str(), "%lf %lf %lf", &la.one, &la.five, &la.fifteen);
    return la;
}

static std::string get_hostname() {
    std::string h = read_file("/etc/hostname");
    return h.empty() ? "unknown" : h;
}

static std::string get_model() {
    std::string m = read_file("/proc/device-tree/model");
    // Strip trailing null bytes that the kernel sometimes appends.
    m.erase(std::remove(m.begin(), m.end(), '\0'), m.end());
    return m.empty() ? "Generic Linux" : m;
}

// ---------------------------------------------------------------------------
// JSON output (hand-rolled to avoid external dependencies)
// ---------------------------------------------------------------------------

static void print_json() {
    auto mem  = get_memory();
    auto disk = get_disk();
    auto la   = get_load();
    double cpu_temp = get_cpu_temp();
    double uptime   = get_uptime();

    std::ostringstream os;
    os << std::fixed << std::setprecision(2);
    os << "{\n";
    os << "  \"version\": \"" << VERSION << "\",\n";
    os << "  \"hostname\": \"" << get_hostname() << "\",\n";
    os << "  \"model\": \"" << get_model() << "\",\n";
    os << "  \"cpu_temp_c\": " << cpu_temp << ",\n";
    os << "  \"uptime_s\": " << uptime << ",\n";
    os << "  \"load_avg\": [" << la.one << ", " << la.five << ", " << la.fifteen << "],\n";
    os << "  \"memory\": {\n";
    os << "    \"total_kb\": " << mem.total_kb << ",\n";
    os << "    \"available_kb\": " << mem.available_kb << "\n";
    os << "  },\n";
    os << "  \"disk\": {\n";
    os << "    \"total_bytes\": " << disk.total_bytes << ",\n";
    os << "    \"free_bytes\": " << disk.free_bytes << "\n";
    os << "  }\n";
    os << "}\n";
    std::cout << os.str();
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main(int argc, char *argv[]) {
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--version") == 0 || std::strcmp(argv[i], "-v") == 0) {
            std::cout << "echosmart-sysinfo " << VERSION << "\n";
            return 0;
        }
        if (std::strcmp(argv[i], "--help") == 0 || std::strcmp(argv[i], "-h") == 0) {
            std::cout << "Usage: echosmart-sysinfo [--version] [--help]\n"
                      << "Print system diagnostics as JSON.\n";
            return 0;
        }
    }
    print_json();
    return 0;
}
