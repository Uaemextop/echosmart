/**
 * echosmart-sensor-read — Read EchoSmart sensors from C++ for fast, low-level
 *                          hardware access on Raspberry Pi OS.
 *
 * Sub-commands:
 *   ds18b20   — Read 1-Wire temperature sensor
 *   dht22     — Read DHT22 temperature + humidity
 *   bh1750    — Read BH1750 light sensor (I2C)
 *   soil      — Read capacitive soil moisture via ADS1115 (I2C)
 *   mhz19c    — Read MH-Z19C CO₂ sensor (UART)
 *
 * Flags:
 *   --simulate   Return random but realistic values (no hardware required)
 *   --json       Output as JSON (default)
 *   --version    Print version and exit
 *   --help       Show usage
 *
 * Build:  cmake gateway/cpp && make
 */

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <string>

#ifndef VERSION
#define VERSION "1.0.0"
#endif

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

static std::mt19937 &rng() {
    static std::mt19937 gen(
        static_cast<unsigned>(
            std::chrono::steady_clock::now().time_since_epoch().count()));
    return gen;
}

static double rand_range(double lo, double hi) {
    std::uniform_real_distribution<double> dist(lo, hi);
    return std::round(dist(rng()) * 10.0) / 10.0;
}

static std::string trim(const std::string &s) {
    auto b = s.find_first_not_of(" \t\n\r");
    if (b == std::string::npos) return "";
    auto e = s.find_last_not_of(" \t\n\r");
    return s.substr(b, e - b + 1);
}

static std::string read_file(const char *path) {
    std::ifstream f(path);
    if (!f.is_open()) return "";
    std::string c((std::istreambuf_iterator<char>(f)),
                   std::istreambuf_iterator<char>());
    return trim(c);
}

// ---------------------------------------------------------------------------
// Sensor readers
// ---------------------------------------------------------------------------

// --- DS18B20 (1-Wire) ---

static int read_ds18b20(bool simulate) {
    double temp = 0.0;
    if (simulate) {
        temp = rand_range(15.0, 35.0);
    } else {
        // Locate the first w1 device
        std::string base = "/sys/bus/w1/devices/";
        FILE *fp = popen("ls /sys/bus/w1/devices/ 2>/dev/null | grep '^28-'", "r");
        if (!fp) {
            std::cerr << "error: cannot access 1-Wire bus\n";
            return 1;
        }
        char buf[128];
        std::string dev;
        if (fgets(buf, sizeof(buf), fp)) dev = trim(std::string(buf));
        pclose(fp);

        if (dev.empty()) {
            std::cerr << "error: no DS18B20 device found on 1-Wire bus\n";
            return 1;
        }

        std::string path = base + dev + "/w1_slave";
        std::string raw  = read_file(path.c_str());
        auto pos = raw.find("t=");
        if (pos == std::string::npos) {
            std::cerr << "error: could not parse DS18B20 output\n";
            return 1;
        }
        temp = std::stod(raw.substr(pos + 2)) / 1000.0;
    }

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "{\"sensor\":\"ds18b20\",\"type\":\"temperature\","
              << "\"value\":" << temp << ",\"unit\":\"°C\"}\n";
    return 0;
}

// --- DHT22 (GPIO) ---

static int read_dht22(bool simulate) {
    double temp = 0.0, hum = 0.0;
    if (simulate) {
        temp = rand_range(15.0, 35.0);
        hum  = rand_range(40.0, 90.0);
    } else {
        // Real read would require bit-banging GPIO; production builds use
        // libgpiod or the kernel driver at /sys/class/gpio.
        std::cerr << "error: DHT22 hardware read not yet implemented in C++ binary; "
                     "use --simulate or the Python driver\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "{\"sensor\":\"dht22\",\"type\":\"temperature_humidity\","
              << "\"temperature\":" << temp << ","
              << "\"humidity\":" << hum << ","
              << "\"unit_temp\":\"°C\",\"unit_hum\":\"%\"}\n";
    return 0;
}

// --- BH1750 (I2C) ---

static int read_bh1750(bool simulate) {
    double lux = 0.0;
    if (simulate) {
        lux = rand_range(100.0, 50000.0);
    } else {
        // I2C address 0x23, continuously high-resolution mode
        const char *dev = "/dev/i2c-1";
        FILE *fp = fopen(dev, "rb");
        if (!fp) {
            std::cerr << "error: cannot open " << dev << "\n";
            return 1;
        }
        // Production would use ioctl I2C_SLAVE + read 2 bytes
        fclose(fp);
        std::cerr << "error: BH1750 hardware read not yet implemented in C++ binary; "
                     "use --simulate or the Python driver\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(0);
    std::cout << "{\"sensor\":\"bh1750\",\"type\":\"light\","
              << "\"value\":" << lux << ",\"unit\":\"lux\"}\n";
    return 0;
}

// --- Capacitive soil moisture (ADS1115 via I2C) ---

static int read_soil(bool simulate) {
    double pct = 0.0;
    if (simulate) {
        pct = rand_range(10.0, 95.0);
    } else {
        std::cerr << "error: Soil moisture hardware read not yet implemented in C++ binary; "
                     "use --simulate or the Python driver\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "{\"sensor\":\"soil_moisture\",\"type\":\"moisture\","
              << "\"value\":" << pct << ",\"unit\":\"%\"}\n";
    return 0;
}

// --- MH-Z19C (UART) ---

static int read_mhz19c(bool simulate) {
    int ppm = 0;
    if (simulate) {
        ppm = static_cast<int>(rand_range(400.0, 2000.0));
    } else {
        const char *port = "/dev/serial0";
        FILE *fp = fopen(port, "rb");
        if (!fp) {
            std::cerr << "error: cannot open " << port << "\n";
            return 1;
        }
        fclose(fp);
        std::cerr << "error: MH-Z19C hardware read not yet implemented in C++ binary; "
                     "use --simulate or the Python driver\n";
        return 1;
    }

    std::cout << "{\"sensor\":\"mhz19c\",\"type\":\"co2\","
              << "\"value\":" << ppm << ",\"unit\":\"ppm\"}\n";
    return 0;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

static void usage() {
    std::cout <<
        "Usage: echosmart-sensor-read <sensor> [--simulate] [--help] [--version]\n"
        "\n"
        "Sensors:\n"
        "  ds18b20   1-Wire temperature sensor\n"
        "  dht22     GPIO temperature + humidity sensor\n"
        "  bh1750    I2C light sensor\n"
        "  soil      Capacitive soil moisture (ADS1115)\n"
        "  mhz19c    UART CO₂ sensor\n"
        "\n"
        "Flags:\n"
        "  --simulate   Return simulated values (no hardware required)\n"
        "  --version    Print version\n"
        "  --help       Show this message\n";
}

int main(int argc, char *argv[]) {
    bool simulate = false;
    std::string sensor;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--simulate" || arg == "-s") {
            simulate = true;
        } else if (arg == "--version" || arg == "-v") {
            std::cout << "echosmart-sensor-read " << VERSION << "\n";
            return 0;
        } else if (arg == "--help" || arg == "-h") {
            usage();
            return 0;
        } else if (arg[0] != '-') {
            sensor = arg;
        }
    }

    if (sensor.empty()) {
        std::cerr << "error: no sensor specified\n\n";
        usage();
        return 1;
    }

    if (sensor == "ds18b20")  return read_ds18b20(simulate);
    if (sensor == "dht22")    return read_dht22(simulate);
    if (sensor == "bh1750")   return read_bh1750(simulate);
    if (sensor == "soil")     return read_soil(simulate);
    if (sensor == "mhz19c")   return read_mhz19c(simulate);

    std::cerr << "error: unknown sensor '" << sensor << "'\n\n";
    usage();
    return 1;
}
