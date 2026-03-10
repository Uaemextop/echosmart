class TestAlerts:
    def _create_sensor(self, client, headers):
        client.post(
            "/api/v1/gateways/",
            json={"gateway_id": "gw-alert", "name": "Alert GW"},
            headers=headers,
        )
        client.post(
            "/api/v1/sensors/",
            json={
                "sensor_id": "s-alert",
                "gateway_id": "gw-alert",
                "name": "Alert Sensor",
                "sensor_type": "DS18B20",
                "unit": "°C",
            },
            headers=headers,
        )

    def test_create_alert_rule(self, client, auth_headers):
        self._create_sensor(client, auth_headers)
        resp = client.post(
            "/api/v1/alert-rules/",
            json={
                "sensor_id": "s-alert",
                "name": "High Temp",
                "condition": "gt",
                "threshold": 40.0,
                "severity": "high",
                "cooldown_minutes": 15,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "High Temp"
        assert data["condition"] == "gt"
        assert data["threshold"] == 40.0
        assert data["is_active"] is True

    def test_list_alert_rules(self, client, auth_headers):
        self._create_sensor(client, auth_headers)
        client.post(
            "/api/v1/alert-rules/",
            json={
                "sensor_id": "s-alert",
                "name": "Rule 1",
                "condition": "gt",
                "threshold": 50.0,
                "severity": "critical",
            },
            headers=auth_headers,
        )
        resp = client.get("/api/v1/alert-rules/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_delete_alert_rule(self, client, auth_headers):
        self._create_sensor(client, auth_headers)
        create_resp = client.post(
            "/api/v1/alert-rules/",
            json={
                "sensor_id": "s-alert",
                "name": "Delete Me",
                "condition": "lt",
                "threshold": 10.0,
                "severity": "low",
            },
            headers=auth_headers,
        )
        rule_id = create_resp.json()["id"]
        resp = client.delete(f"/api/v1/alert-rules/{rule_id}", headers=auth_headers)
        assert resp.status_code == 204

    def test_list_alerts_empty(self, client, auth_headers):
        resp = client.get("/api/v1/alerts/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_acknowledge_alert(self, client, auth_headers, db, tenant, admin_user):
        from src.models.alert import Alert
        from src.models.gateway import Gateway
        from src.models.sensor import Sensor

        gw = Gateway(id="gw-ack", tenant_id=tenant.id, name="Ack GW")
        db.add(gw)
        db.commit()
        sensor = Sensor(
            id="s-ack",
            gateway_id="gw-ack",
            tenant_id=tenant.id,
            type="DS18B20",
            name="Ack Sensor",
            unit="°C",
        )
        db.add(sensor)
        db.commit()
        alert = Alert(
            tenant_id=tenant.id,
            sensor_id="s-ack",
            severity="high",
            message="Temperature too high",
            current_value=45.0,
            threshold=40.0,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        resp = client.post(
            f"/api/v1/alerts/{alert.id}/acknowledge",
            json={"notes": "Checked"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_acknowledged"] is True
        assert resp.json()["acknowledged_by"] == admin_user.id

    def test_viewer_cannot_create_alert_rule(self, client, auth_headers, viewer_headers):
        self._create_sensor(client, auth_headers)
        resp = client.post(
            "/api/v1/alert-rules/",
            json={
                "sensor_id": "s-alert",
                "name": "Viewer Rule",
                "condition": "gt",
                "threshold": 50.0,
                "severity": "high",
            },
            headers=viewer_headers,
        )
        assert resp.status_code == 403
