/**
 * @file cmd_test.cpp
 * @brief Implementation of the "test" command — sensor self-test.
 */

#include "cmd_test.h"

#include "../drivers/driver_factory.h"
#include "../shared/logger.h"

#include <iostream>
#include <string>
#include <vector>

namespace echosmart {

/// Test a single sensor type in simulation mode.
/// Returns true on PASS, false on FAIL.
static bool test_single(const std::string& type) {
    auto driver = DriverFactory::create(type);
    if (!driver) {
        std::cout << "  [FAIL] " << type << " — unknown driver\n";
        return false;
    }

    SensorData reading = driver->read(/*simulate=*/true);
    if (reading.is_valid) {
        std::cout << "  [PASS] " << type
                  << " — " << reading.value << " " << reading.unit;
        if (!reading.secondary_unit.empty()) {
            std::cout << "  |  " << reading.secondary_value
                      << " " << reading.secondary_unit;
        }
        std::cout << "\n";
        return true;
    }

    std::cout << "  [FAIL] " << type << " — read returned invalid data\n";
    return false;
}

// -----------------------------------------------------------------------
// Command entry point
// -----------------------------------------------------------------------

int cmd_test(const CliArgs& args) {
    std::string target = args.input;
    int failures = 0;

    if (target.empty() || target == "all") {
        // Test every supported sensor type.
        std::cout << "Testing all sensor drivers (simulation mode):\n";
        auto types = DriverFactory::list_types();
        for (const auto& t : types) {
            if (!test_single(t)) ++failures;
        }
    } else {
        // Test a single sensor type.
        std::cout << "Testing sensor driver (simulation mode):\n";
        if (!test_single(target)) ++failures;
    }

    std::cout << "\n";
    if (failures == 0) {
        std::cout << "All tests passed.\n";
    } else {
        std::cout << failures << " test(s) failed.\n";
    }

    return failures;
}

} // namespace echosmart
