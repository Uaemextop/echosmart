cmake_minimum_required(VERSION 3.16)
project(echosmart-binaries VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimisation flags for Raspberry Pi
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG")

# --- Shared library (object library to avoid duplicate compilation) ------
add_library(echosmart_shared OBJECT
    shared/sensor_data.cpp
    shared/alert_rule.cpp
    shared/config_loader.cpp
    shared/file_utils.cpp
    shared/json_formatter.cpp
    shared/logger.cpp
)

# --- Drivers (object library) -------------------------------------------
add_library(echosmart_drivers OBJECT
    drivers/sensor_driver.cpp
    drivers/driver_factory.cpp
    drivers/ds18b20_driver.cpp
    drivers/dht22_driver.cpp
    drivers/bh1750_driver.cpp
    drivers/soil_driver.cpp
    drivers/mhz19c_driver.cpp
)
target_include_directories(echosmart_drivers PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# --- Core library (object library) --------------------------------------
add_library(echosmart_core OBJECT
    core/gateway.cpp
    core/sensor_poller.cpp
    core/alert_engine.cpp
    core/data_store.cpp
)
target_include_directories(echosmart_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# --- echosmart (unified CLI) --------------------------------------------
add_executable(echosmart
    main.cpp
    cli.cpp
    commands/cmd_read.cpp
    commands/cmd_sysinfo.cpp
    commands/cmd_run.cpp
    commands/cmd_setup.cpp
    commands/cmd_status.cpp
    commands/cmd_calibrate.cpp
    commands/cmd_list.cpp
    commands/cmd_test.cpp
    commands/cmd_version.cpp
    commands/cmd_help.cpp
)
target_link_libraries(echosmart PRIVATE
    echosmart_core
    echosmart_drivers
    echosmart_shared
)
target_include_directories(echosmart PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# --- Legacy single-file binaries (kept for backward compatibility) ------
add_executable(echosmart-gateway-bin echosmart-gateway.cpp)
target_compile_definitions(echosmart-gateway-bin PRIVATE
    VERSION="${PROJECT_VERSION}"
)
set_target_properties(echosmart-gateway-bin PROPERTIES
    OUTPUT_NAME echosmart-gateway-bin
)

add_executable(echosmart-sysinfo echosmart-sysinfo.cpp)
target_compile_definitions(echosmart-sysinfo PRIVATE
    VERSION="${PROJECT_VERSION}"
)

add_executable(echosmart-sensor-read echosmart-sensor-read.cpp)
target_compile_definitions(echosmart-sensor-read PRIVATE
    VERSION="${PROJECT_VERSION}"
)

# Install targets (used by debian/rules)
install(TARGETS echosmart echosmart-gateway-bin echosmart-sysinfo echosmart-sensor-read
        RUNTIME DESTINATION bin)
