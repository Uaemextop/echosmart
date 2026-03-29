/**
 * @file test_helpers.h
 * @brief Lightweight, assert-based test macros for the EchoSmart CTest suite.
 *
 * No external test framework required — each test binary is a standalone
 * executable that returns 0 on success, 1 on any assertion failure.
 */

#pragma once

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>

// ---------------------------------------------------------------------------
// Test declaration / execution macros
// ---------------------------------------------------------------------------

/// Declare a test function named test_<name>.
#define TEST(name) void test_##name()

/// Run a previously declared test, printing OK or aborting on failure.
#define RUN_TEST(name)                                        \
    do {                                                      \
        std::cout << "  " << #name << "... ";                 \
        test_##name();                                        \
        std::cout << "OK\n";                                  \
    } while (0)

// ---------------------------------------------------------------------------
// Assertion macros — each prints file:line on failure and exits with code 1.
// ---------------------------------------------------------------------------

#define ASSERT_TRUE(cond)                                                     \
    do {                                                                      \
        if (!(cond)) {                                                        \
            std::cerr << "FAIL: " << #cond                                    \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_FALSE(cond) ASSERT_TRUE(!(cond))

#define ASSERT_EQ(a, b)                                                       \
    do {                                                                      \
        if ((a) != (b)) {                                                     \
            std::cerr << "FAIL: " << #a << " != " << #b                       \
                      << " (" << (a) << " vs " << (b) << ")"                  \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_NE(a, b)                                                       \
    do {                                                                      \
        if ((a) == (b)) {                                                     \
            std::cerr << "FAIL: " << #a << " == " << #b                       \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_NEAR(a, b, eps)                                                \
    do {                                                                      \
        if (std::fabs(static_cast<double>(a) - static_cast<double>(b))        \
                > static_cast<double>(eps)) {                                 \
            std::cerr << "FAIL: " << #a << " not near " << #b                 \
                      << " (" << (a) << " vs " << (b) << ", eps=" << (eps)    \
                      << ") at " << __FILE__ << ":" << __LINE__ << "\n";      \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_CONTAINS(str, substr)                                          \
    do {                                                                      \
        const std::string _s(str);                                            \
        const std::string _sub(substr);                                       \
        if (_s.find(_sub) == std::string::npos) {                             \
            std::cerr << "FAIL: '" << _s << "' doesn't contain '"             \
                      << _sub << "'"                                          \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_NOT_NULL(ptr)                                                  \
    do {                                                                      \
        if ((ptr) == nullptr) {                                               \
            std::cerr << "FAIL: " << #ptr << " is null"                       \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_NULL(ptr)                                                      \
    do {                                                                      \
        if ((ptr) != nullptr) {                                               \
            std::cerr << "FAIL: " << #ptr << " is not null"                   \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_GE(a, b)                                                       \
    do {                                                                      \
        if ((a) < (b)) {                                                      \
            std::cerr << "FAIL: " << #a << " < " << #b                        \
                      << " (" << (a) << " vs " << (b) << ")"                  \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)

#define ASSERT_LE(a, b)                                                       \
    do {                                                                      \
        if ((a) > (b)) {                                                      \
            std::cerr << "FAIL: " << #a << " > " << #b                        \
                      << " (" << (a) << " vs " << (b) << ")"                  \
                      << " at " << __FILE__ << ":" << __LINE__ << "\n";       \
            std::exit(1);                                                     \
        }                                                                     \
    } while (0)
