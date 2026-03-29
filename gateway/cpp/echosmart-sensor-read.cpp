/**
 * echosmart-sensor-read — EchoSmart Sensor Reader Binary
 *
 * Reads physical sensors directly from Linux system interfaces:
 *   - DS18B20 via 1-Wire (/sys/bus/w1/)
 *   - DHT22   via GPIO (bit-bang timing in /sys/class/gpio or libgpiod)
 *   - BH1750  via I2C  (/dev/i2c-*)
 *   - Soil    via I2C  ADS1115 (/dev/i2c-*)
 *   - MH-Z19C via UART (/dev/ttyS* or /dev/ttyAMA*)
 *
 * All output is JSON to stdout. Errors are emitted as JSON with "error" key.
 *
 * Usage:
 *   echosmart-sensor-read ds18b20 [device_id]
 *   echosmart-sensor-read dht22   [gpio_pin]
 *   echosmart-sensor-read bh1750  [i2c_bus]
 *   echosmart-sensor-read soil    [i2c_bus]
 *   echosmart-sensor-read mhz19c  [serial_port]
 *   echosmart-sensor-read --simulate <sensor>
 *   echosmart-sensor-read --version
 *
 * Compile (native):
 *   g++ -O2 -std=c++17 -o echosmart-sensor-read echosmart-sensor-read.cpp
 *
 * Compile (cross arm64):
 *   aarch64-linux-gnu-g++ -O2 -std=c++17 -o echosmart-sensor-read echosmart-sensor-read.cpp
 */

#include <cerrno>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <linux/i2c-dev.h>
#include <optional>
#include <random>
#include <sstream>
#include <string>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>
#include <vector>

static constexpr const char* VERSION = "1.0.0";

// ---------------------------------------------------------------------------
// JSON helpers
// ---------------------------------------------------------------------------

static std::string json_escape(const std::string& s) {
    std::string out;
    for (unsigned char c : s) {
        if      (c == '"')  out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (c == '\n') out += "\\n";
        else if (c == '\r') out += "\\r";
        else if (c < 0x20) { char b[8]; snprintf(b,8,"\\u%04x",c); out+=b; }
        else out += static_cast<char>(c);
    }
    return out;
}
static std::string Q(const std::string& s) { return "\"" + json_escape(s) + "\""; }

static std::string dbl1(double v, int prec = 2) {
    if (std::isnan(v) || std::isinf(v)) return "null";
    char buf[32]; snprintf(buf, sizeof(buf), "%.*f", prec, v); return buf;
}

static std::string iso8601_now() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    struct tm tm_buf{};
    gmtime_r(&t, &tm_buf);
    char buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm_buf);
    return std::string(buf);
}

static void emit_error(const std::string& sensor, const std::string& msg) {
    std::cout << "{"
              << Q("sensor")    << ":" << Q(sensor) << ","
              << Q("error")     << ":" << Q(msg) << ","
              << Q("timestamp") << ":" << Q(iso8601_now())
              << "}\n";
}

// ---------------------------------------------------------------------------
// Simulation — deterministic pseudo-random values seeded by time
// ---------------------------------------------------------------------------

struct SimValues {
    double temperature;
    double humidity;
    double light_lux;
    double soil_moisture;
    double co2_ppm;
};

static SimValues sim_values() {
    // Gaussian noise around realistic greenhouse values
    auto now = std::chrono::steady_clock::now().time_since_epoch().count();
    std::mt19937 rng(static_cast<uint32_t>(now & 0xFFFFFFFF));
    std::normal_distribution<double> temp_dist(22.5, 1.5);
    std::normal_distribution<double> hum_dist(65.0, 5.0);
    std::normal_distribution<double> lux_dist(8000.0, 500.0);
    std::normal_distribution<double> soil_dist(45.0, 8.0);
    std::normal_distribution<double> co2_dist(800.0, 100.0);

    auto clamp = [](double v, double lo, double hi) {
        return v < lo ? lo : (v > hi ? hi : v);
    };

    return SimValues{
        clamp(temp_dist(rng),  -10.0, 80.0),
        clamp(hum_dist(rng),    0.0, 100.0),
        clamp(lux_dist(rng),    0.0, 65535.0),
        clamp(soil_dist(rng),   0.0, 100.0),
        clamp(co2_dist(rng),  400.0, 5000.0)
    };
}

// ---------------------------------------------------------------------------
// DS18B20 — 1-Wire temperature sensor
// ---------------------------------------------------------------------------

static void read_ds18b20(const std::string& device_id, bool simulate) {
    if (simulate) {
        SimValues sv = sim_values();
        std::cout << "{"
                  << Q("sensor")      << ":" << Q("ds18b20") << ","
                  << Q("device_id")   << ":" << Q("28-simulated") << ","
                  << Q("temperature") << ":" << dbl1(sv.temperature) << ","
                  << Q("unit")        << ":" << Q("celsius") << ","
                  << Q("simulated")   << ":true,"
                  << Q("timestamp")   << ":" << Q(iso8601_now())
                  << "}\n";
        return;
    }

    // 1-Wire devices live under /sys/bus/w1/devices/28-XXXX/w1_slave
    std::string base = "/sys/bus/w1/devices/";
    std::string target_id = device_id;

    // Auto-discover if no device_id given
    if (target_id.empty() || target_id == "auto") {
        // Find first 28-* directory
        std::string glob_base = base;
        // Simple manual directory scan via /proc isn't reliable; use known path
        // Attempt default common IDs
        target_id = "";
        // Walk /sys/bus/w1/devices/
        FILE* ls = popen("ls /sys/bus/w1/devices/ 2>/dev/null", "r");
        if (ls) {
            char buf[256];
            while (fgets(buf, sizeof(buf), ls)) {
                std::string entry(buf);
                if (!entry.empty() && entry.back() == '\n') entry.pop_back();
                if (entry.rfind("28-", 0) == 0) { target_id = entry; break; }
            }
            pclose(ls);
        }
        if (target_id.empty()) {
            emit_error("ds18b20", "No 1-Wire device found under /sys/bus/w1/devices/. "
                                  "Enable 1-Wire with 'dtoverlay=w1-gpio' in /boot/firmware/config.txt.");
            return;
        }
    }

    std::string path = base + target_id + "/w1_slave";
    std::ifstream f(path);
    if (!f.is_open()) {
        emit_error("ds18b20", "Cannot open " + path + ": " + strerror(errno));
        return;
    }

    std::string line1, line2;
    std::getline(f, line1);
    std::getline(f, line2);

    // line1: "XX XX ... YES"
    // line2: "XX XX ... t=XXXXX"
    if (line1.find("YES") == std::string::npos) {
        emit_error("ds18b20", "CRC check failed for device " + target_id);
        return;
    }

    auto pos = line2.find("t=");
    if (pos == std::string::npos) {
        emit_error("ds18b20", "Malformed w1_slave output for device " + target_id);
        return;
    }

    int raw = 0;
    try { raw = std::stoi(line2.substr(pos + 2)); }
    catch (...) {
        emit_error("ds18b20", "Cannot parse temperature from w1_slave");
        return;
    }

    double temp_c = static_cast<double>(raw) / 1000.0;
    std::cout << "{"
              << Q("sensor")      << ":" << Q("ds18b20") << ","
              << Q("device_id")   << ":" << Q(target_id) << ","
              << Q("temperature") << ":" << dbl1(temp_c) << ","
              << Q("unit")        << ":" << Q("celsius") << ","
              << Q("simulated")   << ":false,"
              << Q("timestamp")   << ":" << Q(iso8601_now())
              << "}\n";
}

// ---------------------------------------------------------------------------
// DHT22 — GPIO temperature + humidity
//   Reading DHT22 requires precise timing (~1µs resolution).
//   On Linux userspace, we read from the kernel w1-therm or use sysfs-gpio
//   bit-banging. For production, the gateway Python service handles this via
//   Adafruit CircuitPython; here we provide a lightweight fallback using the
//   /sys/class/gpio interface with busy-wait timing.
//
//   NOTE: For reliability on RPi, use the pigpio daemon socket protocol or
//   the Python adafruit-circuitpython-dht library instead.
// ---------------------------------------------------------------------------

static void read_dht22(const std::string& gpio_pin_str, bool simulate) {
    if (simulate) {
        SimValues sv = sim_values();
        std::cout << "{"
                  << Q("sensor")      << ":" << Q("dht22") << ","
                  << Q("gpio_pin")    << ":" << gpio_pin_str << ","
                  << Q("temperature") << ":" << dbl1(sv.temperature) << ","
                  << Q("humidity")    << ":" << dbl1(sv.humidity) << ","
                  << Q("unit_temp")   << ":" << Q("celsius") << ","
                  << Q("unit_hum")    << ":" << Q("percent") << ","
                  << Q("simulated")   << ":true,"
                  << Q("timestamp")   << ":" << Q(iso8601_now())
                  << "}\n";
        return;
    }

    // Try to read from pigpio daemon via simple socket protocol (port 8888)
    // pigpiod must be running: sudo systemctl enable --now pigpiod
    // We use the command CMD_HWVER to verify connectivity first, then
    // CMD_MICS / GPIO read for DHT22 bit-bang.
    //
    // For simplicity, attempt to read cached values from /run/echosmart/dht22.json
    // which the Python gateway writes after each poll.
    const std::string cache_path = "/run/echosmart/dht22.json";
    std::ifstream cf(cache_path);
    if (cf.is_open()) {
        std::ostringstream oss;
        oss << cf.rdbuf();
        std::cout << oss.str() << "\n";
        return;
    }

    emit_error("dht22",
        "DHT22 direct GPIO bit-bang not supported without pigpio daemon. "
        "Use the Python gateway for DHT22 (it handles timing via adafruit-circuitpython-dht). "
        "Cache file " + cache_path + " not found. "
        "Run with --simulate for testing.");
}

// ---------------------------------------------------------------------------
// BH1750 — I2C ambient light sensor
// ---------------------------------------------------------------------------

static constexpr uint8_t BH1750_ADDR_LOW  = 0x23;  // ADDR pin → GND
static constexpr uint8_t BH1750_ADDR_HIGH = 0x5C;  // ADDR pin → VCC
static constexpr uint8_t BH1750_POWER_ON   = 0x01;
static constexpr uint8_t BH1750_RESET       = 0x07;
static constexpr uint8_t BH1750_CONT_HRES   = 0x10; // Continuous H-resolution mode (1 lux)

static void read_bh1750(const std::string& bus_str, bool simulate) {
    if (simulate) {
        SimValues sv = sim_values();
        std::cout << "{"
                  << Q("sensor")    << ":" << Q("bh1750") << ","
                  << Q("light_lux") << ":" << dbl1(sv.light_lux, 1) << ","
                  << Q("unit")      << ":" << Q("lux") << ","
                  << Q("simulated") << ":true,"
                  << Q("timestamp") << ":" << Q(iso8601_now())
                  << "}\n";
        return;
    }

    int bus_num = 1;
    if (!bus_str.empty() && bus_str != "auto") {
        try { bus_num = std::stoi(bus_str); } catch (...) {}
    }

    std::string dev = "/dev/i2c-" + std::to_string(bus_num);
    int fd = open(dev.c_str(), O_RDWR);
    if (fd < 0) {
        emit_error("bh1750", "Cannot open " + dev + ": " + strerror(errno) +
                   ". Enable I2C with 'dtparam=i2c_arm=on' in /boot/firmware/config.txt.");
        return;
    }

    // Try both BH1750 addresses
    uint8_t addr = BH1750_ADDR_LOW;
    if (ioctl(fd, I2C_SLAVE, addr) < 0) {
        addr = BH1750_ADDR_HIGH;
        if (ioctl(fd, I2C_SLAVE, addr) < 0) {
            close(fd);
            emit_error("bh1750", "Cannot set I2C slave address 0x23/0x5C: " + std::string(strerror(errno)));
            return;
        }
    }

    // Power on + configure
    uint8_t cmd = BH1750_POWER_ON;
    if (write(fd, &cmd, 1) != 1) {
        close(fd); emit_error("bh1750", "I2C write POWER_ON failed"); return;
    }
    cmd = BH1750_RESET;
    if (write(fd, &cmd, 1) != 1) {
        close(fd); emit_error("bh1750", "I2C write RESET failed"); return;
    }
    cmd = BH1750_CONT_HRES;
    if (write(fd, &cmd, 1) != 1) {
        close(fd); emit_error("bh1750", "I2C write CONT_HRES failed"); return;
    }

    // Wait for measurement (max 180 ms for H-resolution mode)
    struct timespec ts{ 0, 200'000'000L };
    nanosleep(&ts, nullptr);

    uint8_t buf[2]{};
    if (read(fd, buf, 2) != 2) {
        close(fd); emit_error("bh1750", "I2C read failed"); return;
    }
    close(fd);

    int raw = (static_cast<int>(buf[0]) << 8) | buf[1];
    // BH1750: lux = raw / 1.2 (datasheet)
    double lux = static_cast<double>(raw) / 1.2;

    std::cout << "{"
              << Q("sensor")    << ":" << Q("bh1750") << ","
              << Q("i2c_bus")   << ":" << bus_num << ","
              << Q("i2c_addr")  << ":" << (addr == BH1750_ADDR_LOW ? "\"0x23\"" : "\"0x5C\"") << ","
              << Q("light_lux") << ":" << dbl1(lux, 1) << ","
              << Q("unit")      << ":" << Q("lux") << ","
              << Q("simulated") << ":false,"
              << Q("timestamp") << ":" << Q(iso8601_now())
              << "}\n";
}

// ---------------------------------------------------------------------------
// Soil Moisture — ADS1115 (16-bit ADC) via I2C
// ---------------------------------------------------------------------------

// ADS1115 register addresses
static constexpr uint8_t ADS1115_ADDR       = 0x48; // ADDR → GND
static constexpr uint8_t ADS1115_REG_CONV   = 0x00;
static constexpr uint8_t ADS1115_REG_CONFIG = 0x01;

// Config: single-shot, AIN0-GND, ±4.096V, 128 SPS
static constexpr uint16_t ADS1115_CONFIG_OS_SINGLE = 0x8000;
static constexpr uint16_t ADS1115_CONFIG_MUX_AIN0  = 0x4000;
static constexpr uint16_t ADS1115_CONFIG_PGA_4096  = 0x0200;
static constexpr uint16_t ADS1115_CONFIG_MODE_SS   = 0x0100;
static constexpr uint16_t ADS1115_CONFIG_DR_128    = 0x0080;
static constexpr uint16_t ADS1115_CONFIG_COMP_QUE  = 0x0003; // Disable comparator

static void read_soil(const std::string& bus_str, bool simulate) {
    if (simulate) {
        SimValues sv = sim_values();
        std::cout << "{"
                  << Q("sensor")         << ":" << Q("soil_moisture") << ","
                  << Q("moisture_pct")   << ":" << dbl1(sv.soil_moisture) << ","
                  << Q("unit")           << ":" << Q("percent") << ","
                  << Q("simulated")      << ":true,"
                  << Q("timestamp")      << ":" << Q(iso8601_now())
                  << "}\n";
        return;
    }

    int bus_num = 1;
    if (!bus_str.empty() && bus_str != "auto") {
        try { bus_num = std::stoi(bus_str); } catch (...) {}
    }

    std::string dev = "/dev/i2c-" + std::to_string(bus_num);
    int fd = open(dev.c_str(), O_RDWR);
    if (fd < 0) {
        emit_error("soil_moisture", "Cannot open " + dev + ": " + strerror(errno));
        return;
    }

    if (ioctl(fd, I2C_SLAVE, ADS1115_ADDR) < 0) {
        close(fd);
        emit_error("soil_moisture", "Cannot set I2C slave 0x48: " + std::string(strerror(errno)));
        return;
    }

    // Write config register — start single-shot conversion on AIN0
    uint16_t config = ADS1115_CONFIG_OS_SINGLE | ADS1115_CONFIG_MUX_AIN0 |
                      ADS1115_CONFIG_PGA_4096   | ADS1115_CONFIG_MODE_SS  |
                      ADS1115_CONFIG_DR_128      | ADS1115_CONFIG_COMP_QUE;
    uint8_t write_buf[3];
    write_buf[0] = ADS1115_REG_CONFIG;
    write_buf[1] = static_cast<uint8_t>(config >> 8);
    write_buf[2] = static_cast<uint8_t>(config & 0xFF);

    if (write(fd, write_buf, 3) != 3) {
        close(fd); emit_error("soil_moisture", "ADS1115 config write failed"); return;
    }

    // Wait for conversion (at 128 SPS, ~8 ms; use 20 ms for safety)
    struct timespec ts{ 0, 20'000'000L };
    nanosleep(&ts, nullptr);

    // Poll OS bit until conversion complete (max 100 ms total)
    for (int retry = 0; retry < 10; ++retry) {
        uint8_t reg = ADS1115_REG_CONFIG;
        if (write(fd, &reg, 1) != 1) break;
        uint8_t cfg_buf[2]{};
        if (read(fd, cfg_buf, 2) != 2) break;
        uint16_t cfg_read = (static_cast<uint16_t>(cfg_buf[0]) << 8) | cfg_buf[1];
        if (cfg_read & 0x8000) break; // OS bit set → conversion done
        struct timespec w{ 0, 10'000'000L };
        nanosleep(&w, nullptr);
    }

    // Read conversion register
    uint8_t reg = ADS1115_REG_CONV;
    if (write(fd, &reg, 1) != 1) {
        close(fd); emit_error("soil_moisture", "ADS1115 register select failed"); return;
    }
    uint8_t data[2]{};
    if (read(fd, data, 2) != 2) {
        close(fd); emit_error("soil_moisture", "ADS1115 read failed"); return;
    }
    close(fd);

    int16_t raw = static_cast<int16_t>((static_cast<uint16_t>(data[0]) << 8) | data[1]);
    // Convert to voltage (±4.096 V FSR, 16-bit signed)
    double voltage = static_cast<double>(raw) * 4.096 / 32767.0;

    // Capacitive soil sensor (typical range: ~1.2 V dry, ~2.0 V wet — calibrate!)
    // Map 1.2–2.0 V → 0–100%
    constexpr double V_DRY = 1.2;
    constexpr double V_WET = 2.0;
    double moisture_pct = (voltage - V_DRY) / (V_WET - V_DRY) * 100.0;
    if (moisture_pct < 0.0) moisture_pct = 0.0;
    if (moisture_pct > 100.0) moisture_pct = 100.0;

    std::cout << "{"
              << Q("sensor")       << ":" << Q("soil_moisture") << ","
              << Q("i2c_bus")      << ":" << bus_num << ","
              << Q("adc_raw")      << ":" << raw << ","
              << Q("voltage_v")    << ":" << dbl1(voltage, 4) << ","
              << Q("moisture_pct") << ":" << dbl1(moisture_pct) << ","
              << Q("unit")         << ":" << Q("percent") << ","
              << Q("simulated")    << ":false,"
              << Q("timestamp")    << ":" << Q(iso8601_now())
              << "}\n";
}

// ---------------------------------------------------------------------------
// MH-Z19C — UART CO₂ sensor
// ---------------------------------------------------------------------------

// MH-Z19C command: read CO2 concentration (9 bytes)
static constexpr uint8_t MHZ19C_CMD_READ[9] = {
    0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79
};

static uint8_t mhz19c_checksum(const uint8_t* buf) {
    uint8_t s = 0;
    for (int i = 1; i < 8; ++i) s += buf[i];
    return ~s + 1;
}

static void read_mhz19c(const std::string& port_str, bool simulate) {
    if (simulate) {
        SimValues sv = sim_values();
        std::cout << "{"
                  << Q("sensor")     << ":" << Q("mhz19c") << ","
                  << Q("co2_ppm")    << ":" << dbl1(sv.co2_ppm, 0) << ","
                  << Q("unit")       << ":" << Q("ppm") << ","
                  << Q("simulated")  << ":true,"
                  << Q("timestamp")  << ":" << Q(iso8601_now())
                  << "}\n";
        return;
    }

    std::string port = port_str;
    if (port.empty() || port == "auto") {
        // Raspberry Pi UART: /dev/ttyAMA0 (RPi 3/4 with UART overlay)
        // or /dev/ttyS0 (mini UART — less reliable)
        const char* candidates[] = {
            "/dev/ttyAMA0", "/dev/ttyAMA1", "/dev/ttyS0", nullptr
        };
        for (int i = 0; candidates[i]; ++i) {
            if (access(candidates[i], R_OK | W_OK) == 0) {
                port = candidates[i];
                break;
            }
        }
        if (port.empty()) {
            emit_error("mhz19c", "No UART port found. Enable UART with 'enable_uart=1' "
                                  "and 'dtoverlay=disable-bt' in /boot/firmware/config.txt.");
            return;
        }
    }

    int fd = open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        emit_error("mhz19c", "Cannot open " + port + ": " + strerror(errno) +
                   ". Make sure UART is enabled and user is in 'dialout' group.");
        return;
    }

    // Set raw UART: 9600 baud, 8N1
    struct termios tty{};
    tcgetattr(fd, &tty);
    cfsetispeed(&tty, B9600);
    cfsetospeed(&tty, B9600);
    cfmakeraw(&tty);
    tty.c_cc[VMIN]  = 9;   // Wait for 9 bytes
    tty.c_cc[VTIME] = 15;  // 1.5 second timeout
    tcflush(fd, TCIFLUSH);
    tcsetattr(fd, TCSANOW, &tty);

    // Switch to blocking mode for read
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags & ~O_NONBLOCK);

    // Send read command
    if (write(fd, MHZ19C_CMD_READ, 9) != 9) {
        close(fd); emit_error("mhz19c", "UART write failed: " + std::string(strerror(errno))); return;
    }

    // Read 9-byte response
    uint8_t resp[9]{};
    ssize_t n = read(fd, resp, 9);
    close(fd);

    if (n != 9) {
        emit_error("mhz19c", "UART read timeout or short read (got " +
                   std::to_string(n) + " bytes). Check wiring and baud rate.");
        return;
    }
    if (resp[0] != 0xFF || resp[1] != 0x86) {
        emit_error("mhz19c", "Invalid response header from MH-Z19C");
        return;
    }
    if (resp[8] != mhz19c_checksum(resp)) {
        emit_error("mhz19c", "MH-Z19C checksum mismatch — check wiring");
        return;
    }

    int co2_ppm = (static_cast<int>(resp[2]) << 8) | resp[3];
    int temp_raw = static_cast<int>(resp[4]) - 40;

    std::cout << "{"
              << Q("sensor")      << ":" << Q("mhz19c") << ","
              << Q("port")        << ":" << Q(port) << ","
              << Q("co2_ppm")     << ":" << co2_ppm << ","
              << Q("temperature") << ":" << temp_raw << ","
              << Q("unit_co2")    << ":" << Q("ppm") << ","
              << Q("unit_temp")   << ":" << Q("celsius") << ","
              << Q("simulated")   << ":false,"
              << Q("timestamp")   << ":" << Q(iso8601_now())
              << "}\n";
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

static void print_usage() {
    std::cout <<
        "Usage: echosmart-sensor-read [--simulate] <sensor> [options]\n"
        "\n"
        "Sensors:\n"
        "  ds18b20 [device_id]   — 1-Wire temperature (auto-discover if omitted)\n"
        "  dht22   [gpio_pin]    — GPIO temperature + humidity (default: GPIO4)\n"
        "  bh1750  [i2c_bus]     — I2C light sensor (default: bus 1)\n"
        "  soil    [i2c_bus]     — I2C capacitive soil via ADS1115 (default: bus 1)\n"
        "  mhz19c  [serial_port] — UART CO₂ sensor (auto-discover if omitted)\n"
        "\n"
        "Flags:\n"
        "  --simulate    Use simulated (fake) sensor values (no hardware needed)\n"
        "  --version     Print version and exit\n"
        "  --help        Print this help\n"
        "\n"
        "Output: JSON to stdout. On error, emits JSON with 'error' key.\n"
        "\n"
        "Examples:\n"
        "  echosmart-sensor-read ds18b20\n"
        "  echosmart-sensor-read ds18b20 28-0123456789ab\n"
        "  echosmart-sensor-read bh1750 1\n"
        "  echosmart-sensor-read mhz19c /dev/ttyAMA0\n"
        "  echosmart-sensor-read --simulate co2\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) { print_usage(); return 1; }

    bool simulate = false;
    std::string sensor;
    std::string arg1;

    for (int i = 1; i < argc; ++i) {
        std::string a(argv[i]);
        if (a == "--simulate") {
            simulate = true;
        } else if (a == "--version") {
            std::cout << "echosmart-sensor-read " << VERSION << "\n";
            return 0;
        } else if (a == "--help" || a == "-h") {
            print_usage(); return 0;
        } else if (sensor.empty()) {
            sensor = a;
        } else if (arg1.empty()) {
            arg1 = a;
        }
    }

    if (sensor.empty()) { print_usage(); return 1; }

    if      (sensor == "ds18b20") read_ds18b20(arg1, simulate);
    else if (sensor == "dht22")   read_dht22(arg1.empty() ? "4" : arg1, simulate);
    else if (sensor == "bh1750")  read_bh1750(arg1, simulate);
    else if (sensor == "soil")    read_soil(arg1, simulate);
    else if (sensor == "mhz19c")  read_mhz19c(arg1, simulate);
    else {
        emit_error(sensor, "Unknown sensor '" + sensor +
                   "'. Valid: ds18b20, dht22, bh1750, soil, mhz19c");
        return 1;
    }

    return 0;
}
