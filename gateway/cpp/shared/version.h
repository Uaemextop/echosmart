/**
 * @file version.h
 * @brief EchoSmart gateway version constants.
 *
 * Single source of truth for the gateway version.  Include this header
 * wherever the version string is needed — no duplication, no drift.
 */

#pragma once

#define ES_VERSION_MAJOR  1
#define ES_VERSION_MINOR  0
#define ES_VERSION_PATCH  0
#define ES_VERSION_STRING "1.0.0"

namespace echosmart {

/// Returns the compile-time version string (e.g. "1.0.0").
constexpr const char* es_version() { return ES_VERSION_STRING; }

} // namespace echosmart
