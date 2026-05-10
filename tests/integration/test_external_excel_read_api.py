from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from zipfile import ZipFile

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_external_excel_read_api_returns_standard_rows(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    workbook = tmp_path / "standard.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Standard Records",
        rows=[
            ["LTR Number", "Test Item", "Sample Description"],
            ["EIA-364-09", "Insulation resistance", "Housing sample"],
        ],
    )
    try:
        register = client.put(
            "/api/external-resources/standard_record_excel",
            json={"path": str(workbook), "active": True},
        )
        validate = client.post("/api/external-resources/standard_record_excel/validate")
        response = client.get("/api/external-resources/standard-record/rows")

        assert register.status_code == 200
        assert validate.status_code == 200
        assert response.status_code == 200
        payload = response.json()
        assert payload["matched_sheets"] == ["Standard Records"]
        assert payload["rows"][0]["standard_code"] == "EIA-364-09"
        assert payload["rows"][0]["source_sheet"] == "Standard Records"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_excel_read_api_returns_equipment_rows_with_query(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    workbook = tmp_path / "equipment.xlsx"
    _write_minimal_xlsx(
        workbook,
        sheet_name="Equipment Calibration",
        rows=[
            ["Equipment ID", "Equipment Name", "Calibration Due Date"],
            ["EQ-001", "Load Frame", "2026-08-10"],
            ["EQ-002", "Thermal Chamber", "2026-12-01"],
        ],
    )
    try:
        client.put(
            "/api/external-resources/equipment_calibration_excel",
            json={"path": str(workbook), "active": True},
        )
        client.post("/api/external-resources/equipment_calibration_excel/validate")
        response = client.get(
            "/api/external-resources/equipment-calibration/rows",
            params={"query": "thermal"},
        )

        assert response.status_code == 200
        rows = response.json()["rows"]
        assert len(rows) == 1
        assert rows[0]["equipment_id"] == "EQ-002"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_excel_read_api_returns_404_for_unregistered_resource(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        response = client.get("/api/external-resources/standard-record/rows")

        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), engine


def _write_minimal_xlsx(
    path: Path,
    *,
    sheet_name: str,
    rows: list[list[str]],
) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{sheet_name}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
    Target="worksheets/sheet1.xml"/>
</Relationships>""",
        )
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))


def _sheet_xml(rows: list[list[str]]) -> str:
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row):
            reference = f"{chr(65 + column_index)}{row_index}"
            cells.append(
                f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>'
            )
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        "</worksheet>"
    )
