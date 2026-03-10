from datetime import date


class TestReports:
    def test_generate_report(self, client, auth_headers):
        resp = client.post(
            "/api/v1/reports/generate",
            json={
                "title": "Monthly Report",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "sensors": ["sensor-1", "sensor-2"],
                "format": "pdf",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert "report_id" in data

    def test_list_reports(self, client, auth_headers):
        client.post(
            "/api/v1/reports/generate",
            json={
                "title": "Report 1",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "sensors": ["s1"],
                "format": "pdf",
            },
            headers=auth_headers,
        )
        resp = client.get("/api/v1/reports/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_report(self, client, auth_headers):
        create_resp = client.post(
            "/api/v1/reports/generate",
            json={
                "title": "Get Report",
                "date_from": "2024-02-01",
                "date_to": "2024-02-28",
                "sensors": ["s1"],
                "format": "excel",
            },
            headers=auth_headers,
        )
        report_id = create_resp.json()["report_id"]
        resp = client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Get Report"
        assert resp.json()["format"] == "excel"

    def test_get_report_not_found(self, client, auth_headers):
        resp = client.get(
            "/api/v1/reports/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_viewer_cannot_generate_report(self, client, viewer_headers):
        resp = client.post(
            "/api/v1/reports/generate",
            json={
                "title": "Viewer Report",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "sensors": ["s1"],
                "format": "pdf",
            },
            headers=viewer_headers,
        )
        assert resp.status_code == 403

    def test_generate_report_excel(self, client, auth_headers):
        resp = client.post(
            "/api/v1/reports/generate",
            json={
                "title": "Excel Report",
                "date_from": "2024-03-01",
                "date_to": "2024-03-31",
                "sensors": ["s1", "s2", "s3"],
                "format": "excel",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
