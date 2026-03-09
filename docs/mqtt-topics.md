# MQTT Topics

EchoSmart uses Mosquitto as its MQTT broker. All sensor communication passes through the following topic structure.

---

## Topics

### `/sensors/{uuid}/data`

Published by the **Gateway** when a sensor submits a reading via `POST /sensors/{uuid}/data`.

**Direction:** Gateway → Backend  
**QoS:** 1  
**Retained:** No

#### Payload Schema

```json
{
  "uuid": "sensor-abc-123",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "temperature": 24.5,
  "humidity": 65.2,
  "co2": 412.0,
  "light": 850.0,
  "soil_moisture": 42.1,
  "battery_level": 87
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uuid` | string | yes | Unique sensor identifier |
| `timestamp` | ISO 8601 | yes | Reading timestamp |
| `temperature` | float | no | Temperature in °C |
| `humidity` | float | no | Relative humidity % |
| `co2` | float | no | CO₂ concentration in ppm |
| `light` | float | no | Light intensity in lux |
| `soil_moisture` | float | no | Soil moisture % |
| `battery_level` | integer | no | Battery level % |

---

### `/sensors/{uuid}/config`

Published by the **Backend** when a config update is requested via `PUT /api/sensors/{id}/config`.

**Direction:** Backend → Gateway → Sensor  
**QoS:** 1  
**Retained:** Yes (so reconnecting sensors receive latest config)

#### Payload Schema

```json
{
  "sampling_interval_seconds": 30,
  "alert_thresholds": {
    "temperature_max": 35.0,
    "temperature_min": 10.0,
    "humidity_max": 90.0
  },
  "enabled": true,
  "firmware_update_url": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sampling_interval_seconds` | integer | no | How often to publish readings |
| `alert_thresholds` | object | no | Local alert thresholds on sensor |
| `enabled` | boolean | no | Enable/disable data publishing |
| `firmware_update_url` | string/null | no | OTA firmware update URL |

---

## Example curl (publish data via gateway REST)

```bash
curl -X POST http://localhost:8000/sensors/sensor-abc-123/data \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": 24.5,
      "humidity": 65.2,
      "co2": 412.0,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }'
```

## Example curl (update sensor config)

```bash
curl -X PUT http://localhost:3000/api/sensors/{sensor_id}/config \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sampling_interval_seconds": 60,
    "enabled": true
  }'
```
