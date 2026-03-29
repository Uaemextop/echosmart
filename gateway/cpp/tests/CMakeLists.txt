# --------------------------------------------------------------------------
# CTest suite for the EchoSmart gateway C++ code.
#
# Each test is a standalone executable that returns 0 on success.
# No external test framework is required — tests use simple assert macros
# defined in test_helpers.h.
# --------------------------------------------------------------------------

enable_testing()

# Common include path: parent cpp/ directory so that
# #include "../shared/xxx.h" and friends resolve correctly.
set(ES_CPP_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/..)
include_directories(${ES_CPP_ROOT})

# -----------------------------------------------------------------------
# 1. test_json_formatter — shared only
# -----------------------------------------------------------------------
add_executable(test_json_formatter
    test_json_formatter.cpp
)
target_link_libraries(test_json_formatter PRIVATE echosmart_shared)
target_include_directories(test_json_formatter PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_json_formatter COMMAND test_json_formatter)

# -----------------------------------------------------------------------
# 2. test_sensor_data — shared only
# -----------------------------------------------------------------------
add_executable(test_sensor_data
    test_sensor_data.cpp
)
target_link_libraries(test_sensor_data PRIVATE echosmart_shared)
target_include_directories(test_sensor_data PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_sensor_data COMMAND test_sensor_data)

# -----------------------------------------------------------------------
# 3. test_alert_rule — shared only
# -----------------------------------------------------------------------
add_executable(test_alert_rule
    test_alert_rule.cpp
)
target_link_libraries(test_alert_rule PRIVATE echosmart_shared)
target_include_directories(test_alert_rule PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_alert_rule COMMAND test_alert_rule)

# -----------------------------------------------------------------------
# 4. test_config_loader — shared only
# -----------------------------------------------------------------------
add_executable(test_config_loader
    test_config_loader.cpp
)
target_link_libraries(test_config_loader PRIVATE echosmart_shared)
target_include_directories(test_config_loader PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_config_loader COMMAND test_config_loader)

# -----------------------------------------------------------------------
# 5. test_drivers — shared + drivers
# -----------------------------------------------------------------------
add_executable(test_drivers
    test_drivers.cpp
)
target_link_libraries(test_drivers PRIVATE echosmart_drivers echosmart_shared)
target_include_directories(test_drivers PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_drivers COMMAND test_drivers)

# -----------------------------------------------------------------------
# 6. test_alert_engine — shared + drivers + core
# -----------------------------------------------------------------------
add_executable(test_alert_engine
    test_alert_engine.cpp
)
target_link_libraries(test_alert_engine PRIVATE
    echosmart_core echosmart_drivers echosmart_shared
)
target_include_directories(test_alert_engine PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_alert_engine COMMAND test_alert_engine)

# -----------------------------------------------------------------------
# 7. test_gateway_cycle — shared + drivers + core
# -----------------------------------------------------------------------
add_executable(test_gateway_cycle
    test_gateway_cycle.cpp
)
target_link_libraries(test_gateway_cycle PRIVATE
    echosmart_core echosmart_drivers echosmart_shared
)
target_include_directories(test_gateway_cycle PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_gateway_cycle COMMAND test_gateway_cycle)

# -----------------------------------------------------------------------
# 8. test_cli — shared + cli.cpp (needs cli.o)
# -----------------------------------------------------------------------
add_executable(test_cli
    test_cli.cpp
    ${ES_CPP_ROOT}/cli.cpp
)
target_link_libraries(test_cli PRIVATE echosmart_shared)
target_include_directories(test_cli PRIVATE ${ES_CPP_ROOT})
add_test(NAME test_cli COMMAND test_cli)
