/**
 * @file data_store.cpp
 * @brief Implementation of the append-only local data store.
 */

#include "data_store.h"

#include "../shared/json_formatter.h"
#include "../shared/logger.h"

#include <chrono>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>

namespace fs = std::filesystem;

namespace echosmart {

// -----------------------------------------------------------------------
// Construction
// -----------------------------------------------------------------------

DataStore::DataStore(const std::string& base_dir)
    : base_dir_(base_dir) {}

// -----------------------------------------------------------------------
// Date stamp
// -----------------------------------------------------------------------

std::string DataStore::today_stamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm{};

#if defined(_WIN32)
    localtime_s(&tm, &t);
#else
    localtime_r(&t, &tm);
#endif

    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y%m%d");
    return oss.str();
}

// -----------------------------------------------------------------------
// File I/O
// -----------------------------------------------------------------------

void DataStore::append_line(const std::string& path, const std::string& line) {
    // Ensure parent directory exists.
    fs::path p(path);
    if (p.has_parent_path()) {
        std::error_code ec;
        fs::create_directories(p.parent_path(), ec);
        // Silently ignore errors (e.g. permission denied).
    }

    std::ofstream ofs(path, std::ios::app);
    if (ofs) {
        ofs << line << "\n";
    }
}

// -----------------------------------------------------------------------
// Save operations
// -----------------------------------------------------------------------

void DataStore::save(const SensorData& data) {
    std::string filename = "readings-" + today_stamp() + ".jsonl";
    std::string path = base_dir_ + "/" + filename;
    append_line(path, data.to_json());
}

void DataStore::save_alert(const AlertRule& rule, const SensorData& data) {
    std::string filename = "alerts-" + today_stamp() + ".jsonl";
    std::string path = base_dir_ + "/" + filename;

    std::string json = json_object({
        json_string("sensor_type", data.sensor_type),
        json_string("sensor_name", data.sensor_name),
        json_number("value", data.value, 2),
        json_string("unit", data.unit),
        json_int("timestamp_ms", data.timestamp_ms),
        json_string("severity", severity_to_string(rule.severity)),
        json_string("condition", condition_to_string(rule.condition)),
        json_number("threshold", rule.threshold, 2),
        json_string("message", rule.message)
    });

    append_line(path, json);
}

// -----------------------------------------------------------------------
// Pending count
// -----------------------------------------------------------------------

int DataStore::pending_count() const {
    std::string filename = "readings-" + today_stamp() + ".jsonl";
    std::string path = base_dir_ + "/" + filename;

    std::ifstream ifs(path);
    if (!ifs) return 0;

    int count = 0;
    std::string line;
    while (std::getline(ifs, line)) {
        if (!line.empty()) ++count;
    }
    return count;
}

// -----------------------------------------------------------------------
// Cleanup
// -----------------------------------------------------------------------

void DataStore::cleanup(int keep_days) {
    std::error_code ec;
    if (!fs::exists(base_dir_, ec)) return;

    auto now = std::chrono::system_clock::now();
    auto cutoff = now - std::chrono::hours(24 * keep_days);
    auto cutoff_time = std::chrono::system_clock::to_time_t(cutoff);

    for (const auto& entry : fs::directory_iterator(base_dir_, ec)) {
        if (!entry.is_regular_file()) continue;

        std::string name = entry.path().filename().string();
        // Only clean up our own files (readings-*.jsonl, alerts-*.jsonl).
        if (name.find("readings-") != 0 && name.find("alerts-") != 0) continue;
        if (name.find(".jsonl") == std::string::npos) continue;

        // Extract date from the filename (e.g. "readings-20260101.jsonl").
        // This avoids clock-domain conversion issues across C++ stdlib versions.
        std::string date_part;
        auto dash = name.find('-');
        auto dot  = name.find('.', dash);
        if (dash != std::string::npos && dot != std::string::npos) {
            date_part = name.substr(dash + 1, dot - dash - 1);
        }
        if (date_part.size() != 8) continue;

        // Parse YYYYMMDD into a time_t for comparison.
        std::tm file_tm{};
        file_tm.tm_year = std::atoi(date_part.substr(0, 4).c_str()) - 1900;
        file_tm.tm_mon  = std::atoi(date_part.substr(4, 2).c_str()) - 1;
        file_tm.tm_mday = std::atoi(date_part.substr(6, 2).c_str());
        std::time_t file_time_t = std::mktime(&file_tm);

        if (file_time_t < cutoff_time) {
            fs::remove(entry.path(), ec);
            if (!ec) {
                log_info("Cleaned up old data file: " + name);
            }
        }
    }
}

} // namespace echosmart
