/**
 * echosmart-sysinfo — EchoSmart System Diagnostics Binary
 *
 * Reads CPU usage, RAM, disk, CPU temperature, uptime, hostname, and OS
 * version from Linux system interfaces and emits structured JSON to stdout.
 *
 * Usage:
 *   echosmart-sysinfo            → JSON to stdout
 *   echosmart-sysinfo --pretty   → pretty-printed JSON
 *   echosmart-sysinfo --version  → prints version string
 *
 * Compile (native):
 *   g++ -O2 -std=c++17 -o echosmart-sysinfo echosmart-sysinfo.cpp
 *
 * Compile (cross arm64):
 *   aarch64-linux-gnu-g++ -O2 -std=c++17 -o echosmart-sysinfo echosmart-sysinfo.cpp
 */

#include <chrono>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <sys/statvfs.h>
#include <sys/sysinfo.h>
#include <sys/utsname.h>
#include <unistd.h>

static constexpr const char* VERSION = "1.0.0";

// ---------------------------------------------------------------------------
// Helpers — JSON escaping
// ---------------------------------------------------------------------------

static std::string json_escape(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 4);
    for (unsigned char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (c < 0x20) {
                    char buf[8];
                    snprintf(buf, sizeof(buf), "\\u%04x", c);
                    out += buf;
                } else {
                    out += static_cast<char>(c);
                }
        }
    }
    return out;
}

static std::string quoted(const std::string& s) {
    return "\"" + json_escape(s) + "\"";
}

// ---------------------------------------------------------------------------
// System data readers
// ---------------------------------------------------------------------------

/**
 * Reads CPU usage percentage by comparing two /proc/stat snapshots 100 ms apart.
 * Returns -1.0 on failure.
 */
static double read_cpu_usage() {
    struct CpuStats { long long user, nice, system, idle, iowait, irq, softirq; };

    auto parse_stat = [](CpuStats& s) -> bool {
        std::ifstream f("/proc/stat");
        if (!f.is_open()) return false;
        std::string label;
        f >> label >> s.user >> s.nice >> s.system >> s.idle
          >> s.iowait >> s.irq >> s.softirq;
        return label == "cpu";
    };

    CpuStats s1{}, s2{};
    if (!parse_stat(s1)) return -1.0;

    // Sleep 100 ms for delta measurement
    struct timespec ts{ 0, 100'000'000L };
    nanosleep(&ts, nullptr);

    if (!parse_stat(s2)) return -1.0;

    long long idle1 = s1.idle + s1.iowait;
    long long idle2 = s2.idle + s2.iowait;
    long long total1 = s1.user + s1.nice + s1.system + idle1 + s1.irq + s1.softirq;
    long long total2 = s2.user + s2.nice + s2.system + idle2 + s2.irq + s2.softirq;

    long long dt = total2 - total1;
    if (dt <= 0) return 0.0;

    long long di = idle2 - idle1;
    return 100.0 * (1.0 - static_cast<double>(di) / static_cast<double>(dt));
}

/**
 * Reads CPU temperature from the Raspberry Pi thermal zone.
 * Returns -1.0 on failure.
 */
static double read_cpu_temp() {
    // Standard Linux thermal zone (RPi + most ARM SBCs)
    const char* paths[] = {
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/hwmon/hwmon0/temp1_input",
        nullptr
    };
    for (int i = 0; paths[i]; ++i) {
        std::ifstream f(paths[i]);
        if (!f.is_open()) continue;
        long raw = 0;
        if (f >> raw) return static_cast<double>(raw) / 1000.0;
    }
    return -1.0;
}

/**
 * Reads hostname from the kernel.
 */
static std::string read_hostname() {
    char buf[256]{};
    if (gethostname(buf, sizeof(buf) - 1) == 0) return std::string(buf);
    return "unknown";
}

/**
 * Reads OS information via uname(2).
 */
static std::string read_os_version() {
    // Try /etc/os-release first (human-readable distro name)
    std::ifstream f("/etc/os-release");
    if (f.is_open()) {
        std::string line;
        while (std::getline(f, line)) {
            if (line.rfind("PRETTY_NAME=", 0) == 0) {
                std::string val = line.substr(12);
                // Strip surrounding quotes if present
                if (!val.empty() && val.front() == '"') val = val.substr(1);
                if (!val.empty() && val.back()  == '"') val.pop_back();
                return val;
            }
        }
    }

    // Fallback to uname
    struct utsname u{};
    if (uname(&u) == 0) {
        return std::string(u.sysname) + " " + u.release;
    }
    return "unknown";
}

/**
 * Reads kernel version string.
 */
static std::string read_kernel() {
    struct utsname u{};
    if (uname(&u) == 0) return std::string(u.release);
    return "unknown";
}

/**
 * Reads system uptime in seconds from /proc/uptime.
 */
static long long read_uptime_seconds() {
    std::ifstream f("/proc/uptime");
    if (!f.is_open()) return -1;
    double up = 0;
    f >> up;
    return static_cast<long long>(up);
}

/**
 * Formats uptime into a human-readable string: "Xd Xh Xm Xs"
 */
static std::string format_uptime(long long sec) {
    if (sec < 0) return "unknown";
    long long d = sec / 86400;
    sec %= 86400;
    long long h = sec / 3600;
    sec %= 3600;
    long long m = sec / 60;
    long long s = sec % 60;
    char buf[64];
    snprintf(buf, sizeof(buf), "%lldd %02lldh %02lldm %02llds", d, h, m, s);
    return std::string(buf);
}

struct MemInfo {
    long long total_kb   = -1;
    long long available_kb = -1;
    long long used_kb    = -1;
    double    used_pct   = -1.0;
};

/**
 * Reads memory information from /proc/meminfo.
 */
static MemInfo read_memory() {
    MemInfo mi;
    std::ifstream f("/proc/meminfo");
    if (!f.is_open()) return mi;

    std::string key;
    long long val;
    std::string unit;

    while (f >> key >> val) {
        // Consume optional unit
        std::getline(f, unit);
        if (key == "MemTotal:")     mi.total_kb     = val;
        if (key == "MemAvailable:") mi.available_kb = val;
    }

    if (mi.total_kb > 0 && mi.available_kb >= 0) {
        mi.used_kb  = mi.total_kb - mi.available_kb;
        mi.used_pct = 100.0 * static_cast<double>(mi.used_kb) /
                      static_cast<double>(mi.total_kb);
    }
    return mi;
}

struct DiskInfo {
    long long total_bytes = -1;
    long long used_bytes  = -1;
    long long free_bytes  = -1;
    double    used_pct    = -1.0;
};

/**
 * Reads disk usage for the root filesystem.
 */
static DiskInfo read_disk(const char* path = "/") {
    DiskInfo di;
    struct statvfs sv{};
    if (statvfs(path, &sv) != 0) return di;

    di.total_bytes = static_cast<long long>(sv.f_blocks) * sv.f_frsize;
    di.free_bytes  = static_cast<long long>(sv.f_bfree)  * sv.f_frsize;
    di.used_bytes  = di.total_bytes - di.free_bytes;
    if (di.total_bytes > 0)
        di.used_pct = 100.0 * static_cast<double>(di.used_bytes) /
                      static_cast<double>(di.total_bytes);
    return di;
}

/**
 * Returns ISO-8601 UTC timestamp.
 */
static std::string iso8601_now() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    struct tm tm_buf{};
    gmtime_r(&t, &tm_buf);
    char buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm_buf);
    return std::string(buf);
}

// ---------------------------------------------------------------------------
// JSON renderer
// ---------------------------------------------------------------------------

static std::string build_json(bool pretty) {
    const char* sep  = pretty ? ",\n" : ",";
    const char* kvsep = pretty ? ": " : ":";
    const char* ind1 = pretty ? "  " : "";
    const char* ind2 = pretty ? "    " : "";
    const char* nl   = pretty ? "\n" : "";

    double cpu = read_cpu_usage();
    double temp = read_cpu_temp();
    MemInfo mem = read_memory();
    DiskInfo disk = read_disk("/");
    long long uptime_s = read_uptime_seconds();

    auto dbl2 = [](double v) -> std::string {
        if (v < 0) return "null";
        char buf[32];
        snprintf(buf, sizeof(buf), "%.2f", v);
        return buf;
    };
    auto llstr = [](long long v) -> std::string {
        if (v < 0) return "null";
        return std::to_string(v);
    };

    std::ostringstream o;
    o << "{" << nl
      << ind1 << quoted("timestamp")   << kvsep << quoted(iso8601_now()) << sep << nl
      << ind1 << quoted("version")     << kvsep << quoted(VERSION) << sep << nl
      << ind1 << quoted("hostname")    << kvsep << quoted(read_hostname()) << sep << nl
      << ind1 << quoted("os")          << kvsep << quoted(read_os_version()) << sep << nl
      << ind1 << quoted("kernel")      << kvsep << quoted(read_kernel()) << sep << nl
      << ind1 << quoted("uptime_sec")  << kvsep << llstr(uptime_s) << sep << nl
      << ind1 << quoted("uptime_human")<< kvsep << quoted(format_uptime(uptime_s)) << sep << nl
      << ind1 << quoted("cpu") << kvsep << "{" << nl
      << ind2 << quoted("usage_pct")   << kvsep << dbl2(cpu) << nl
      << ind1 << "}" << sep << nl
      << ind1 << quoted("temperature") << kvsep << "{" << nl
      << ind2 << quoted("cpu_celsius") << kvsep << dbl2(temp) << nl
      << ind1 << "}" << sep << nl
      << ind1 << quoted("memory") << kvsep << "{" << nl
      << ind2 << quoted("total_kb")    << kvsep << llstr(mem.total_kb) << sep << nl
      << ind2 << quoted("used_kb")     << kvsep << llstr(mem.used_kb) << sep << nl
      << ind2 << quoted("available_kb")<< kvsep << llstr(mem.available_kb) << sep << nl
      << ind2 << quoted("used_pct")    << kvsep << dbl2(mem.used_pct) << nl
      << ind1 << "}" << sep << nl
      << ind1 << quoted("disk") << kvsep << "{" << nl
      << ind2 << quoted("path")        << kvsep << quoted("/") << sep << nl
      << ind2 << quoted("total_bytes") << kvsep << llstr(disk.total_bytes) << sep << nl
      << ind2 << quoted("used_bytes")  << kvsep << llstr(disk.used_bytes) << sep << nl
      << ind2 << quoted("free_bytes")  << kvsep << llstr(disk.free_bytes) << sep << nl
      << ind2 << quoted("used_pct")    << kvsep << dbl2(disk.used_pct) << nl
      << ind1 << "}" << nl
      << "}" << nl;

    return o.str();
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main(int argc, char* argv[]) {
    bool pretty = false;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--pretty") == 0) {
            pretty = true;
        } else if (strcmp(argv[i], "--version") == 0) {
            std::cout << "echosmart-sysinfo " << VERSION << "\n";
            return 0;
        } else if (strcmp(argv[i], "--help") == 0) {
            std::cout << "Usage: echosmart-sysinfo [--pretty] [--version]\n"
                      << "  Emits system diagnostics as JSON to stdout.\n";
            return 0;
        }
    }

    std::cout << build_json(pretty);
    return 0;
}
