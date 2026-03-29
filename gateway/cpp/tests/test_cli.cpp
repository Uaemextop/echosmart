/**
 * @file test_cli.cpp
 * @brief Tests for the CLI argument parser and CliArgs accessors.
 */

#include "test_helpers.h"
#include "../cli.h"

using namespace echosmart;

/// Helper: build an argv-style array from a vector of strings.
static CliArgs parse(std::vector<std::string> tokens) {
    std::vector<char*> argv;
    argv.reserve(tokens.size());
    for (auto& t : tokens) argv.push_back(t.data());
    return parse_args(static_cast<int>(argv.size()), argv.data());
}

TEST(command_only) {
    auto a = parse({"echosmart", "status"});
    ASSERT_EQ(a.command, std::string("status"));
    ASSERT_TRUE(a.input.empty());
    ASSERT_TRUE(a.options.empty());
}

TEST(command_with_input) {
    auto a = parse({"echosmart", "read", "ds18b20"});
    ASSERT_EQ(a.command, std::string("read"));
    ASSERT_EQ(a.input, std::string("ds18b20"));
}

TEST(key_value_option) {
    auto a = parse({"echosmart", "status", "--format=json"});
    ASSERT_EQ(a.command, std::string("status"));
    ASSERT_TRUE(a.has("format"));
    ASSERT_EQ(a.get("format"), std::string("json"));
}

TEST(flag_option) {
    auto a = parse({"echosmart", "read", "--simulate"});
    ASSERT_TRUE(a.has("simulate"));
    ASSERT_TRUE(a.get_bool("simulate"));
}

TEST(has_returns_false_for_missing) {
    auto a = parse({"echosmart", "read"});
    ASSERT_FALSE(a.has("nonexistent"));
}

TEST(get_returns_default) {
    auto a = parse({"echosmart", "read"});
    ASSERT_EQ(a.get("missing", "fallback"), std::string("fallback"));
}

TEST(get_bool_defaults) {
    auto a = parse({"echosmart", "read"});
    ASSERT_FALSE(a.get_bool("verbose"));
    ASSERT_TRUE(a.get_bool("verbose", true));
}

TEST(get_int_parses) {
    auto a = parse({"echosmart", "run", "--interval=30"});
    ASSERT_EQ(a.get_int("interval"), 30);
}

TEST(get_int_default_on_missing) {
    auto a = parse({"echosmart", "run"});
    ASSERT_EQ(a.get_int("interval", 60), 60);
}

int main() {
    std::cout << "test_cli\n";
    RUN_TEST(command_only);
    RUN_TEST(command_with_input);
    RUN_TEST(key_value_option);
    RUN_TEST(flag_option);
    RUN_TEST(has_returns_false_for_missing);
    RUN_TEST(get_returns_default);
    RUN_TEST(get_bool_defaults);
    RUN_TEST(get_int_parses);
    RUN_TEST(get_int_default_on_missing);
    std::cout << "[PASS] test_cli\n";
    return 0;
}
