/**
 * @file json_formatter.h
 * @brief Minimal, dependency-free JSON string builder for the EchoSmart gateway.
 *
 * Produces valid JSON without any external library.  Designed for
 * serialisation only — there is no JSON parser here; config_loader
 * and sensor_data handle their own minimal parsing.
 *
 * All values are pre-formatted as strings and composed via json_object().
 */

#pragma once

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace echosmart {

// -----------------------------------------------------------------------
// Primitive field formatters
// -----------------------------------------------------------------------

/// Format a key-value pair where the value is a JSON string.
/// The value is properly escaped (quotes, backslashes, control chars).
/// Example: json_string("name", "Hall \"A\"")  →  "name":"Hall \"A\""
std::string json_string(const std::string& key, const std::string& value);

/// Format a key-value pair where the value is a floating-point number.
/// @p precision controls the number of decimal places (default 2).
/// Example: json_number("temp", 23.456, 1)  →  "temp":23.5
std::string json_number(const std::string& key, double value, int precision = 2);

/// Format a key-value pair where the value is a 64-bit integer.
/// Example: json_int("ts", 1711699200000)  →  "ts":1711699200000
std::string json_int(const std::string& key, int64_t value);

/// Format a key-value pair where the value is a boolean.
/// Example: json_bool("ok", true)  →  "ok":true
std::string json_bool(const std::string& key, bool value);

// -----------------------------------------------------------------------
// Composite formatters
// -----------------------------------------------------------------------

/// Build a JSON object from a list of pre-formatted field strings.
/// Each element in @p fields should come from one of the primitives above.
/// Example: json_object({json_string("a","b"), json_int("n",1)})
///          →  {"a":"b","n":1}
std::string json_object(const std::vector<std::string>& fields);

/// Build a JSON array from a list of pre-formatted element strings.
/// Each element may be a primitive, an object, or another array.
/// Example: json_array({"1","2","3"})  →  [1,2,3]
std::string json_array(const std::vector<std::string>& items);

// -----------------------------------------------------------------------
// Escaping
// -----------------------------------------------------------------------

/// Escape a raw string for safe inclusion inside a JSON string literal.
/// Handles: \" \\ \n \r \t
std::string json_escape(const std::string& raw);

} // namespace echosmart
