from fastapi.testclient import TestClient

from backend.api.main import app


def test_ltr_workbook_password_route_is_not_public() -> None:
    client = TestClient(app)
    path = "/api/settings/ltr-workbook-password"

    assert client.get(path).status_code == 404
    assert client.put(path, json={}).status_code == 404
    assert path not in client.get("/openapi.json").json()["paths"]
