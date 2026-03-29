cmake_minimum_required(VERSION 3.16)
project(echosmart-binaries VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimisation flags for Raspberry Pi
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG")

# --- echosmart-sysinfo -------------------------------------------------
add_executable(echosmart-sysinfo echosmart-sysinfo.cpp)
target_compile_definitions(echosmart-sysinfo PRIVATE
    VERSION="${PROJECT_VERSION}"
)

# --- echosmart-sensor-read ---------------------------------------------
add_executable(echosmart-sensor-read echosmart-sensor-read.cpp)
target_compile_definitions(echosmart-sensor-read PRIVATE
    VERSION="${PROJECT_VERSION}"
)

# Install targets (used by debian/rules)
install(TARGETS echosmart-sysinfo echosmart-sensor-read
        RUNTIME DESTINATION bin)
