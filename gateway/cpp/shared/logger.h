/**
 * @file logger.h
 * @brief Lightweight, dependency-free logging for the EchoSmart gateway.
 *
 * Features:
 *   - Five severity levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
 *   - ISO 8601 timestamps.
 *   - Writes INFO/DEBUG/WARNING to stdout; ERROR/CRITICAL to stderr.
 *   - Runtime-configurable minimum level via set_log_level().
 *
 * Thread safety: each call is self-contained (no shared mutable buffers),
 * but concurrent writes to the same stream rely on the underlying OS
 * line-buffering guarantees.
 */

#pragma once

#include <string>

namespace echosmart {

// -----------------------------------------------------------------------
// Log levels (ordered by increasing severity)
// -----------------------------------------------------------------------

enum class LogLevel {
    DEBUG    = 0,
    INFO     = 1,
    WARNING  = 2,
    ERROR    = 3,
    CRITICAL = 4
};

// -----------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------

/// Set the minimum severity that will be emitted.
void set_log_level(LogLevel level);

/// Return the current minimum level.
LogLevel get_log_level();

/// Parse a human-readable level name (case-insensitive).
/// Returns LogLevel::INFO for unrecognised input.
LogLevel parse_log_level(const std::string& name);

// -----------------------------------------------------------------------
// Logging functions
// -----------------------------------------------------------------------

void log_debug(const std::string& message);
void log_info(const std::string& message);
void log_warning(const std::string& message);
void log_error(const std::string& message);
void log_critical(const std::string& message);

// -----------------------------------------------------------------------
// Utility
// -----------------------------------------------------------------------

/// Returns the current local time formatted as ISO 8601 (no timezone).
/// Example: "2026-03-29T08:00:00"
std::string now_iso8601();

} // namespace echosmart
