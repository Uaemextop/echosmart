import uuid


class TestGatewayCRUD:
    def test_create_gateway(self, client, auth_headers):
        resp = client.post(
            "/api/v1/gateways/",
            json={
                "gateway_id": "gw-001",
                "name": "Main Gateway",
                "location": "Building A",
                "description": "Primary gateway",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "gw-001"
        assert data["name"] == "Main Gateway"
        assert data["status"] == "offline"

    def test_create_gateway_duplicate(self, client, auth_headers):
        payload = {"gateway_id": "gw-dup", "name": "Gateway"}
        client.post("/api/v1/gateways/", json=payload, headers=auth_headers)
        resp = client.post("/api/v1/gateways/", json=payload, headers=auth_headers)
        assert resp.status_code == 409

    def test_list_gateways(self, client, auth_headers):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-list-1", "name": "GW1"},
            headers=auth_headers,
        )
        resp = client.get("/api/v1/gateways/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_get_gateway(self, client, auth_headers):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-get", "name": "GW Get"},
            headers=auth_headers,
        )
        resp = client.get("/api/v1/gateways/gw-get", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == "gw-get"
        assert "sensors_count" in resp.json()

    def test_get_gateway_not_found(self, client, auth_headers):
        resp = client.get("/api/v1/gateways/nonexistent", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_gateway(self, client, auth_headers):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-upd", "name": "Old Name"},
            headers=auth_headers,
        )
        resp = client.put(
            "/api/v1/gateways/gw-upd",
            json={"name": "New Name", "status": "online"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["status"] == "online"

    def test_delete_gateway(self, client, auth_headers):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-del", "name": "To Delete"},
            headers=auth_headers,
        )
        resp = client.delete("/api/v1/gateways/gw-del", headers=auth_headers)
        assert resp.status_code == 204

        resp = client.get("/api/v1/gateways/gw-del", headers=auth_headers)
        assert resp.status_code == 404

    def test_viewer_cannot_create_gateway(self, client, viewer_headers):
        resp = client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-view", "name": "Viewer GW"},
            headers=viewer_headers,
        )
        assert resp.status_code == 403

    def test_ingest_readings(self, client, auth_headers):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-ingest", "name": "Ingest GW"},
            headers=auth_headers,
        )
        resp = client.post(
            "/api/v1/gateways/gw-ingest/readings",
            json={
                "readings": [
                    {"sensor_id": "s1", "value": 23.5, "unit": "°C"},
                    {"sensor_id": "s2", "value": 65.0, "unit": "%"},
                ]
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["readings_ingested"] == 2

    def test_list_gateways_pagination(self, client, auth_headers):
        for i in range(3):
            client.post(
                "/api/v1/gateways/",
                json={"gateway_id": f"gw-page-{i}", "name": f"GW {i}"},
                headers=auth_headers,
            )
        resp = client.get(
            "/api/v1/gateways/?page=1&limit=2", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
