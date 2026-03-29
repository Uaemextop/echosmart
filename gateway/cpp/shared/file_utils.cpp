/**
 * @file file_utils.cpp
 * @brief Implementation of file I/O and string utilities.
 */

#include "file_utils.h"

#include <filesystem>
#include <fstream>
#include <iterator>
#include <sstream>

namespace echosmart {

// -----------------------------------------------------------------------
// File I/O
// -----------------------------------------------------------------------

std::string read_file(const std::string& path) {
    std::ifstream stream(path, std::ios::in);
    if (!stream.is_open()) return "";

    return std::string(
        std::istreambuf_iterator<char>(stream),
        std::istreambuf_iterator<char>());
}

bool write_file(const std::string& path, const std::string& content) {
    std::ofstream stream(path, std::ios::out | std::ios::trunc);
    if (!stream.is_open()) return false;

    stream << content;
    return stream.good();
}

bool file_exists(const std::string& path) {
    std::error_code ec;
    return std::filesystem::exists(path, ec);
}

// -----------------------------------------------------------------------
// String utilities
// -----------------------------------------------------------------------

std::string trim(const std::string& s) {
    constexpr const char* kWhitespace = " \t\n\r";

    const auto first = s.find_first_not_of(kWhitespace);
    if (first == std::string::npos) return "";

    const auto last = s.find_last_not_of(kWhitespace);
    return s.substr(first, last - first + 1);
}

std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::istringstream stream(s);
    std::string token;

    while (std::getline(stream, token, delimiter)) {
        tokens.push_back(token);
    }

    return tokens;
}

// -----------------------------------------------------------------------
// System information
// -----------------------------------------------------------------------

static const char* const kHostnamePath    = "/etc/hostname";
static const char* const kMacAddressPath  = "/sys/class/net/eth0/address";
static const char* const kDefaultHostname = "unknown";
static const char* const kDefaultMac      = "00:00:00:00:00:00";

std::string get_hostname() {
    std::string content = read_file(kHostnamePath);
    std::string hostname = trim(content);
    return hostname.empty() ? kDefaultHostname : hostname;
}

std::string get_mac_address() {
    std::string content = read_file(kMacAddressPath);
    std::string mac = trim(content);
    return mac.empty() ? kDefaultMac : mac;
}

} // namespace echosmart
