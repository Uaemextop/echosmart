/**
 * @file logger.cpp
 * @brief Implementation of the EchoSmart logging subsystem.
 */

#include "logger.h"

#include <algorithm>
#include <cctype>
#include <ctime>
#include <iostream>

namespace echosmart {

// -----------------------------------------------------------------------
// Module-level state
// -----------------------------------------------------------------------

static LogLevel g_min_level = LogLevel::INFO;

// -----------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------

void set_log_level(LogLevel level) {
    g_min_level = level;
}

LogLevel get_log_level() {
    return g_min_level;
}

LogLevel parse_log_level(const std::string& name) {
    std::string upper;
    upper.reserve(name.size());
    for (char ch : name) {
        upper.push_back(static_cast<char>(std::toupper(static_cast<unsigned char>(ch))));
    }

    if (upper == "DEBUG")    return LogLevel::DEBUG;
    if (upper == "INFO")     return LogLevel::INFO;
    if (upper == "WARNING")  return LogLevel::WARNING;
    if (upper == "WARN")     return LogLevel::WARNING;
    if (upper == "ERROR")    return LogLevel::ERROR;
    if (upper == "CRITICAL") return LogLevel::CRITICAL;
    if (upper == "FATAL")    return LogLevel::CRITICAL;

    return LogLevel::INFO;  // safe default
}

// -----------------------------------------------------------------------
// Timestamp
// -----------------------------------------------------------------------

std::string now_iso8601() {
    std::time_t now = std::time(nullptr);
    std::tm     local_tm{};

    // localtime_r is POSIX-safe; fall back to localtime on other platforms.
#if defined(_WIN32)
    localtime_s(&local_tm, &now);
#else
    localtime_r(&now, &local_tm);
#endif

    constexpr int kTimestampBufferSize = 32;
    char buf[kTimestampBufferSize];
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S", &local_tm);
    return std::string(buf);
}

// -----------------------------------------------------------------------
// Internals
// -----------------------------------------------------------------------

static const char* level_tag(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG:    return "[DEBUG]";
        case LogLevel::INFO:     return "[INFO] ";
        case LogLevel::WARNING:  return "[WARN] ";
        case LogLevel::ERROR:    return "[ERROR]";
        case LogLevel::CRITICAL: return "[CRIT] ";
    }
    return "[?????]";
}

static bool should_log(LogLevel level) {
    return static_cast<int>(level) >= static_cast<int>(g_min_level);
}

static std::ostream& stream_for(LogLevel level) {
    if (level >= LogLevel::ERROR) return std::cerr;
    return std::cout;
}

/// Core emit function — all public log_*() helpers delegate here.
static void emit(LogLevel level, const std::string& message) {
    if (!should_log(level)) return;

    std::ostream& out = stream_for(level);
    out << now_iso8601() << " " << level_tag(level) << " " << message << "\n";
    out.flush();
}

// -----------------------------------------------------------------------
// Public API
// -----------------------------------------------------------------------

void log_debug(const std::string& message)    { emit(LogLevel::DEBUG,    message); }
void log_info(const std::string& message)     { emit(LogLevel::INFO,     message); }
void log_warning(const std::string& message)  { emit(LogLevel::WARNING,  message); }
void log_error(const std::string& message)    { emit(LogLevel::ERROR,    message); }
void log_critical(const std::string& message) { emit(LogLevel::CRITICAL, message); }

} // namespace echosmart
