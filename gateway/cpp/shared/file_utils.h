/**
 * @file file_utils.h
 * @brief File I/O and string utilities for the EchoSmart gateway.
 *
 * Consolidates the helper functions that were previously duplicated
 * across echosmart-gateway.cpp, echosmart-sensor-read.cpp, and
 * echosmart-sysinfo.cpp.  Uses C++17 <filesystem> where appropriate.
 */

#pragma once

#include <string>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// File I/O
// -----------------------------------------------------------------------

/// Read the entire contents of a text file into a string.
/// Returns an empty string if the file cannot be opened.
std::string read_file(const std::string& path);

/// Write @p content to @p path, creating or overwriting the file.
/// Returns true on success.
bool write_file(const std::string& path, const std::string& content);

/// Check whether a file (or directory) exists at @p path.
bool file_exists(const std::string& path);

// -----------------------------------------------------------------------
// String utilities
// -----------------------------------------------------------------------

/// Strip leading and trailing whitespace (space, tab, CR, LF).
std::string trim(const std::string& s);

/// Split @p s on every occurrence of @p delimiter.
/// Two consecutive delimiters produce an empty element.
std::vector<std::string> split(const std::string& s, char delimiter);

// -----------------------------------------------------------------------
// System information
// -----------------------------------------------------------------------

/// Returns the system hostname (reads /etc/hostname, falls back to "unknown").
std::string get_hostname();

/// Returns the MAC address of eth0 (reads /sys/class/net/eth0/address).
/// Returns "00:00:00:00:00:00" if the file is not accessible.
std::string get_mac_address();

} // namespace echosmart
