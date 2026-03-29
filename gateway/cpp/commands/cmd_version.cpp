/**
 * @file cmd_version.cpp
 * @brief Implementation of the "version" command.
 */

#include "cmd_version.h"

#include "../shared/version.h"

#include <iostream>

namespace echosmart {

int cmd_version(const CliArgs& /*args*/) {
    std::cout << "echosmart v" << es_version() << "\n";
    return 0;
}

} // namespace echosmart
