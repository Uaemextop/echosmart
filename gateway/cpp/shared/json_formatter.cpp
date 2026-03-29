/**
 * @file json_formatter.cpp
 * @brief Implementation of the minimal JSON string builder.
 */

#include "json_formatter.h"

#include <iomanip>
#include <sstream>

namespace echosmart {

// -----------------------------------------------------------------------
// Escaping
// -----------------------------------------------------------------------

std::string json_escape(const std::string& raw) {
    std::string out;
    out.reserve(raw.size() + 8);  // small head-room for escapes

    for (char ch : raw) {
        switch (ch) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:   out += ch;     break;
        }
    }

    return out;
}

// -----------------------------------------------------------------------
// Primitive field formatters
// -----------------------------------------------------------------------

std::string json_string(const std::string& key, const std::string& value) {
    return "\"" + json_escape(key) + "\":\"" + json_escape(value) + "\"";
}

std::string json_number(const std::string& key, double value, int precision) {
    std::ostringstream oss;
    oss << "\"" << json_escape(key) << "\":"
        << std::fixed << std::setprecision(precision) << value;
    return oss.str();
}

std::string json_int(const std::string& key, int64_t value) {
    return "\"" + json_escape(key) + "\":" + std::to_string(value);
}

std::string json_bool(const std::string& key, bool value) {
    return "\"" + json_escape(key) + "\":" + (value ? "true" : "false");
}

// -----------------------------------------------------------------------
// Composite formatters
// -----------------------------------------------------------------------

std::string json_object(const std::vector<std::string>& fields) {
    std::string result = "{";

    for (size_t i = 0; i < fields.size(); ++i) {
        if (i > 0) result += ",";
        result += fields[i];
    }

    result += "}";
    return result;
}

std::string json_array(const std::vector<std::string>& items) {
    std::string result = "[";

    for (size_t i = 0; i < items.size(); ++i) {
        if (i > 0) result += ",";
        result += items[i];
    }

    result += "]";
    return result;
}

} // namespace echosmart
