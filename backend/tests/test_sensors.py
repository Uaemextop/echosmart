class TestSensorCRUD:
    def _create_gateway(self, client, headers, gw_id="gw-sensor-test"):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": gw_id, "name": "Sensor Test GW"},
            headers=headers,
        )

    def test_create_sensor(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        resp = client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "temp-001",
                "gateway_id": "gw-sensor-test",
                "name": "Temp Sensor",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "temp-001"
        assert data["type"] == "DS18B20"
        assert data["status"] == "active"

    def test_create_sensor_auto_id(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        resp = client.post(
            "/api/v1/sensors/",
            json={
                "gateway_id": "gw-sensor-test",
                "name": "Auto Sensor",
                "sensor_type": "DHT22",
                "unit": "%",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["id"]  # auto-generated UUID

    def test_list_sensors(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-list-1",
                "gateway_id": "gw-sensor-test",
                "name": "Sensor 1",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=auth_headers,
        )
        resp = client.get("/api/v1/sensors/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_sensors_by_gateway(self, client, auth_headers):
        self._create_gateway(client, auth_headers, "gw-a")
        self._create_gateway(client, auth_headers, "gw-b")
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "sa-1",
                "gateway_id": "gw-a",
                "name": "SA1",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=auth_headers,
        )
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "sb-1",
                "gateway_id": "gw-b",
                "name": "SB1",
                "sensor_type": "DHT22",
                "unit": "%",
            },
            headers=auth_headers,
        )
        resp = client.get(
            "/api/v1/sensors/?gateway_id=gw-a", headers=auth_headers
        )
        assert resp.status_code == 200
        assert all(s["gateway_id"] == "gw-a" for s in resp.json())

    def test_get_sensor(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-get",
                "gateway_id": "gw-sensor-test",
                "name": "Get Sensor",
                "sensor_type": "BH1750",
                "unit": "lux",
            },
            headers=auth_headers,
        )
        resp = client.get("/api/v1/sensors/s-get", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Sensor"

    def test_get_sensor_not_found(self, client, auth_headers):
        resp = client.get("/api/v1/sensors/nonexistent", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_sensor(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-upd",
                "gateway_id": "gw-sensor-test",
                "name": "Old Sensor",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=auth_headers,
        )
        resp = client.put(
            "/api/v1/sensors/s-upd",
            json={"name": "Updated Sensor", "polling_interval": 120},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Sensor"
        assert resp.json()["polling_interval"] == 120

    def test_delete_sensor(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-del",
                "gateway_id": "gw-sensor-test",
                "name": "Del Sensor",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=auth_headers,
        )
        resp = client.delete("/api/v1/sensors/s-del", headers=auth_headers)
        assert resp.status_code == 204

        resp = client.get("/api/v1/sensors/s-del", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_sensor_readings(self, client, auth_headers):
        self._create_gateway(client, auth_headers)
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-readings",
                "gateway_id": "gw-sensor-test",
                "name": "Readings Sensor",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=auth_headers,
        )
        resp = client.get(
            "/api/v1/sensors/s-readings/readings", headers=auth_headers
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_viewer_cannot_create_sensor(self, client, auth_headers, viewer_headers):
        self._create_gateway(client, auth_headers)
        resp = client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-viewer",
                "gateway_id": "gw-sensor-test",
                "name": "Viewer Sensor",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=viewer_headers,
        )
        assert resp.status_code == 403
