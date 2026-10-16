from tests.integration.test_existing_projects_api import client


def test_current_workspace_is_actual_connection_and_exposes_no_settings_secrets(client,tmp_path):
    response=client.get("/api/workspace/info")
    assert response.status_code == 200,response.text
    value=response.json()
    assert value["database_path"] == ":memory:"
    assert value["sqlite_user_version"] == 0
    assert value["schema_status"] == "unversioned"
    assert "password" not in response.text.lower()
    assert not (tmp_path/"unused.sqlite3").exists()

