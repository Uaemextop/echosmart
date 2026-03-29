/**
 * @file driver_factory.cpp
 * @brief Implementation of the sensor driver factory.
 */

#include "driver_factory.h"

#include "bh1750_driver.h"
#include "dht22_driver.h"
#include "ds18b20_driver.h"
#include "mhz19c_driver.h"
#include "soil_driver.h"

#include "../shared/logger.h"

namespace echosmart {

std::unique_ptr<SensorDriver> DriverFactory::create(const std::string& type) {
    if (type == "ds18b20") {
        return std::make_unique<DS18B20Driver>();
    }
    if (type == "dht22") {
        return std::make_unique<DHT22Driver>();
    }
    if (type == "bh1750") {
        return std::make_unique<BH1750Driver>();
    }
    if (type == "soil_moisture" || type == "soil") {
        return std::make_unique<SoilDriver>();
    }
    if (type == "mhz19c") {
        return std::make_unique<MHZ19CDriver>();
    }

    log_error("DriverFactory: unknown sensor type '" + type + "'");
    return nullptr;
}

std::vector<std::string> DriverFactory::list_types() {
    return {"bh1750", "dht22", "ds18b20", "mhz19c", "soil_moisture"};
}

} // namespace echosmart
