# EchoSmart FakeNTP

HTTP-based time server for IoT devices that cannot reach standard NTP servers
(port 123/UDP) or operate behind restrictive firewalls.

## Why?

Standard NTP uses **port 123 (UDP)** which requires root access and cannot be
opened on shared hosting. FakeNTP provides the same time synchronization over
**HTTP/HTTPS** (ports 80/443), accessible from any network.

## Quick Start

```bash
# Run locally (default: 0.0.0.0:8123)
python fakentp.py

# Custom host/port
python fakentp.py --host 127.0.0.1 --port 9000
```

## API Endpoints

| Endpoint          | Response Type | Description                        |
|-------------------|---------------|------------------------------------|
| `GET /`           | HTML          | Web UI with live clock             |
| `GET /time`       | JSON          | Full time data (unix + iso + date) |
| `GET /time?fmt=unix` | text/plain | Unix timestamp (e.g. `1711756800.123456`) |
| `GET /time?fmt=iso`  | text/plain | ISO 8601 (e.g. `2026-03-30T00:00:00.000000Z`) |
| `GET /health`     | JSON          | Health check (`{"status":"ok"}`)   |

### JSON Response Example

```json
{
  "unix": 1711756800.123456,
  "iso": "2026-03-30T00:00:00.123456Z",
  "date": "2026-03-30",
  "time": "00:00:00.123456",
  "timezone": "UTC",
  "server": "EchoSmart FakeNTP",
  "version": "1.0.0"
}
```

## IoT Device Usage

### ESP32 (MicroPython)

```python
import urequests
import ujson
import time

r = urequests.get("https://ntp.echosmart.me/time")
data = ujson.loads(r.text)
epoch = int(data["unix"])
# Set RTC or use epoch directly
```

### ESP32 (Arduino / C++)

```cpp
#include <HTTPClient.h>
#include <ArduinoJson.h>

HTTPClient http;
http.begin("https://ntp.echosmart.me/time");
int code = http.GET();
if (code == 200) {
    JsonDocument doc;
    deserializeJson(doc, http.getString());
    double unix_ts = doc["unix"];
    // Use unix_ts to set internal clock
}
http.end();
```

### curl

```bash
# JSON
curl https://ntp.echosmart.me/time

# Unix timestamp only
curl https://ntp.echosmart.me/time?fmt=unix

# ISO 8601 only
curl https://ntp.echosmart.me/time?fmt=iso
```

## Deployment

### Shared Hosting (cPanel) — PHP version

On shared hosting where Python daemons cannot run, a PHP equivalent is provided
at `hosting/ntp/`. Deploy to the `ntp.echosmart.me` subdomain directory:

```bash
# cPanel: create subdomain ntp.echosmart.me → public_html/ntp.echosmart.me/
# Then upload the PHP files:
scp -P 21098 hosting/ntp/* eduardoc3677@68.65.123.247:~/public_html/ntp.echosmart.me/
```

### VPS / Dedicated Server

```bash
# Run as systemd service
python fakentp.py --port 8123

# Behind nginx reverse proxy:
# server_name ntp.echosmart.me;
# location / { proxy_pass http://127.0.0.1:8123; }
```

## Requirements

- Python 3.7+ (stdlib only, no external dependencies)
