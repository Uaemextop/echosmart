cmake_minimum_required(VERSION 3.16)
project(EchoSmartGateway VERSION 1.0.0 LANGUAGES CXX)

# ---------------------------------------------------------------------------
# Build settings
# ---------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Default build type
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags: optimize for release, strict warnings
add_compile_options(
  -O2
  -Wall
  -Wextra
  -Wpedantic
  -Wno-unused-parameter
)

# ARM64 cross-compilation support
# Set via: cmake -DCMAKE_TOOLCHAIN_FILE=toolchain-aarch64.cmake ..
# Or via CMAKE_C_COMPILER / CMAKE_CXX_COMPILER env vars in CI

# ---------------------------------------------------------------------------
# Target: echosmart-sysinfo
# ---------------------------------------------------------------------------
add_executable(echosmart-sysinfo
  echosmart-sysinfo.cpp
)

target_compile_definitions(echosmart-sysinfo PRIVATE
  ECHOSMART_VERSION="${PROJECT_VERSION}"
)

# No external dependencies — pure Linux syscalls + POSIX
install(TARGETS echosmart-sysinfo
  RUNTIME DESTINATION usr/bin
)

# ---------------------------------------------------------------------------
# Target: echosmart-sensor-read
# ---------------------------------------------------------------------------
add_executable(echosmart-sensor-read
  echosmart-sensor-read.cpp
)

target_compile_definitions(echosmart-sensor-read PRIVATE
  ECHOSMART_VERSION="${PROJECT_VERSION}"
)

# Linux i2c-dev header is needed; install with: apt-get install libi2c-dev
# The header linux/i2c-dev.h is part of linux-headers (always present on RPi OS)
install(TARGETS echosmart-sensor-read
  RUNTIME DESTINATION usr/bin
)

# ---------------------------------------------------------------------------
# Install: strip binaries in Release mode to reduce size
# ---------------------------------------------------------------------------
if(CMAKE_BUILD_TYPE STREQUAL "Release")
  add_custom_command(TARGET echosmart-sysinfo     POST_BUILD COMMAND ${CMAKE_STRIP} $<TARGET_FILE:echosmart-sysinfo>)
  add_custom_command(TARGET echosmart-sensor-read POST_BUILD COMMAND ${CMAKE_STRIP} $<TARGET_FILE:echosmart-sensor-read>)
endif()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
message(STATUS "")
message(STATUS "=== EchoSmart Gateway C++ Binaries ===")
message(STATUS "  Version:      ${PROJECT_VERSION}")
message(STATUS "  Build type:   ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ standard: C++${CMAKE_CXX_STANDARD}")
message(STATUS "  Compiler:     ${CMAKE_CXX_COMPILER}")
message(STATUS "  System:       ${CMAKE_SYSTEM_NAME} ${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "  Targets:")
message(STATUS "    - echosmart-sysinfo     → /usr/bin/echosmart-sysinfo")
message(STATUS "    - echosmart-sensor-read → /usr/bin/echosmart-sensor-read")
message(STATUS "")
