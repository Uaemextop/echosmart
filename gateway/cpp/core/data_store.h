/**
 * @file data_store.h
 * @brief Append-only local data store for sensor readings and alerts.
 *
 * Each day's readings are stored in a JSONL file (one JSON object per
 * line).  Old files are removed by cleanup().
 */

#pragma once

#include "../shared/alert_rule.h"
#include "../shared/sensor_data.h"

#include <string>

namespace echosmart {

class DataStore {
public:
    /// Construct a data store rooted at @p base_dir.
    explicit DataStore(const std::string& base_dir = "/var/lib/echosmart");

    /// Append a sensor reading to today's readings-YYYYMMDD.jsonl.
    void save(const SensorData& data);

    /// Append a triggered alert to today's alerts-YYYYMMDD.jsonl.
    void save_alert(const AlertRule& rule, const SensorData& data);

    /// Count lines (pending readings) in today's readings file.
    int pending_count() const;

    /// Delete data files older than @p keep_days.
    void cleanup(int keep_days = 30);

private:
    std::string base_dir_;

    /// Return today's date as "YYYYMMDD".
    static std::string today_stamp();

    /// Append a single line to a file, creating it if necessary.
    static void append_line(const std::string& path, const std::string& line);
};

} // namespace echosmart
