/**
 * @file test_json_formatter.cpp
 * @brief Tests for the json_formatter utility functions.
 */

#include "test_helpers.h"
#include "../shared/json_formatter.h"

using namespace echosmart;

TEST(json_object_produces_valid_json) {
    auto result = json_object({json_string("a", "b"), json_int("n", 1)});
    ASSERT_TRUE(result.front() == '{');
    ASSERT_TRUE(result.back() == '}');
    ASSERT_CONTAINS(result, "\"a\":\"b\"");
    ASSERT_CONTAINS(result, "\"n\":1");
}

TEST(json_object_empty) {
    auto result = json_object({});
    ASSERT_EQ(result, std::string("{}"));
}

TEST(json_string_escapes_quotes) {
    auto result = json_string("k", "say \"hello\"");
    ASSERT_CONTAINS(result, "\\\"hello\\\"");
}

TEST(json_string_escapes_backslash) {
    auto result = json_string("k", "path\\to");
    ASSERT_CONTAINS(result, "path\\\\to");
}

TEST(json_string_escapes_newline) {
    auto result = json_string("k", "line1\nline2");
    ASSERT_CONTAINS(result, "\\n");
}

TEST(json_number_respects_precision) {
    auto result = json_number("v", 23.456, 1);
    ASSERT_CONTAINS(result, "23.5");
}

TEST(json_number_default_precision) {
    auto result = json_number("v", 1.0);
    ASSERT_CONTAINS(result, "\"v\":");
}

TEST(json_int_no_decimal) {
    auto result = json_int("ts", 1711699200000LL);
    ASSERT_CONTAINS(result, "1711699200000");
    ASSERT_TRUE(result.find('.') == std::string::npos);
}

TEST(json_bool_true) {
    auto result = json_bool("ok", true);
    ASSERT_CONTAINS(result, "true");
    ASSERT_TRUE(result.find("\"true\"") == std::string::npos);
}

TEST(json_bool_false) {
    auto result = json_bool("ok", false);
    ASSERT_CONTAINS(result, "false");
}

TEST(json_array_empty) {
    auto result = json_array({});
    ASSERT_EQ(result, std::string("[]"));
}

TEST(json_array_single) {
    auto result = json_array({"42"});
    ASSERT_EQ(result, std::string("[42]"));
}

TEST(json_array_multiple) {
    auto result = json_array({"1", "2", "3"});
    ASSERT_EQ(result, std::string("[1,2,3]"));
}

int main() {
    std::cout << "test_json_formatter\n";
    RUN_TEST(json_object_produces_valid_json);
    RUN_TEST(json_object_empty);
    RUN_TEST(json_string_escapes_quotes);
    RUN_TEST(json_string_escapes_backslash);
    RUN_TEST(json_string_escapes_newline);
    RUN_TEST(json_number_respects_precision);
    RUN_TEST(json_number_default_precision);
    RUN_TEST(json_int_no_decimal);
    RUN_TEST(json_bool_true);
    RUN_TEST(json_bool_false);
    RUN_TEST(json_array_empty);
    RUN_TEST(json_array_single);
    RUN_TEST(json_array_multiple);
    std::cout << "[PASS] test_json_formatter\n";
    return 0;
}
