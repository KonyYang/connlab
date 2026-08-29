from __future__ import annotations

import json

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
    ProjectBasicInformationSampleRow,
    ProjectBasicInformationVersionConflictError,
)
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.repositories.project_basic_information import (
    ProjectBasicInformationRepository,
)


def test_project_basic_information_repository_creates_and_updates_draft() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        repository.save_draft(
            _record(
                "draft-1",
                status="draft",
                version=0,
                values={"project_type": "NPD"},
                updated_at="2026-06-20T09:00:00+00:00",
            )
        )
        repository.save_draft(
            _record(
                "draft-1",
                status="draft",
                version=0,
                values={"project_type": "PEX"},
                updated_at="2026-06-20T10:00:00+00:00",
            )
        )

        draft = repository.get_latest_draft("P1")

    assert draft is not None
    assert draft.record_id == "draft-1"
    assert draft.values == {"project_type": "PEX"}
    assert draft.updated_at == "2026-06-20T10:00:00+00:00"


def test_project_basic_information_repository_creates_multiple_confirmed_versions() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        first = repository.create_confirmed(
            _record(
                "confirmed-1",
                status="confirmed",
                version=1,
                values={"project_type": "NPD"},
            )
        )
        second = repository.create_confirmed(
            _record(
                "confirmed-2",
                status="confirmed",
                version=2,
                values={"project_type": "PEX"},
            )
        )

        latest = repository.get_latest_confirmed("P1")
        versions = repository.list_confirmed_by_project("P1")

    assert versions == [first, second]
    assert latest == second
    assert latest is not None
    assert latest.values["project_type"] == "PEX"


def test_project_basic_information_repository_round_trips_quantity_defaults() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    values = {
        "project_type": "NPD",
        "test_points_per_sample": "3",
        "readings_per_point": "2",
        "contact_points_per_sample": "4",
    }
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        repository.save_draft(
            _record("draft-1", status="draft", version=0, values=values)
        )
        repository.create_confirmed(
            _record("confirmed-1", status="confirmed", version=1, values=values)
        )

        draft = repository.get_latest_draft("P1")
        confirmed = repository.get_latest_confirmed("P1")

    assert draft is not None
    assert draft.values == values
    assert confirmed is not None
    assert confirmed.values == values


def test_project_basic_information_repository_round_trips_confirmed_sample_rows() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    rows = (
        ProjectBasicInformationSampleRow(
            product_name="Pin",
            part_number="PN-1",
            lot_or_traceability="LOT-1",
            material="C1100",
            plating="Ag",
            lubricant="No",
            housing_material="NA",
            quantity=2,
            row_index=0,
            source_form_id="F1",
        ),
    )
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)
        repository.create_confirmed(
            _record(
                "confirmed-1",
                status="confirmed",
                version=1,
                values={"project_type": "NPD"},
                sample_rows=rows,
            )
        )

        confirmed = repository.get_latest_confirmed("P1")

    assert confirmed is not None
    assert confirmed.sample_rows == rows


def test_project_basic_information_repository_returns_next_confirmed_version() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        assert repository.next_confirmed_version("P1") == 1
        repository.create_confirmed(
            _record("confirmed-1", status="confirmed", version=1, values={})
        )

        assert repository.next_confirmed_version("P1") == 2


def test_project_basic_information_repository_translates_duplicate_version() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)
        repository.create_confirmed(
            _record("confirmed-1", status="confirmed", version=1, values={})
        )

        try:
            repository.create_confirmed(
                _record("confirmed-duplicate", status="confirmed", version=1, values={})
            )
        except ProjectBasicInformationVersionConflictError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("Expected duplicate confirmed version to fail")


def test_init_db_creates_project_basic_information_records_table() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)

    init_db(engine)

    assert inspect(engine).has_table("project_basic_information_records") is True


def test_init_db_migrates_legacy_report_sample_authority_columns() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE sample_infos (
                sample_id VARCHAR(64) PRIMARY KEY,
                project_id VARCHAR(64) NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                part_number VARCHAR(255) NOT NULL,
                revision VARCHAR(64),
                lot_or_traceability VARCHAR(255),
                material VARCHAR(255),
                plating VARCHAR(255),
                housing_material VARCHAR(255),
                quantity INTEGER
            )
            """
        )
        connection.exec_driver_sql(
            "INSERT INTO sample_infos (sample_id, project_id, product_name, part_number) "
            "VALUES ('S2', 'P1', 'Socket', 'PN-2'), ('S1', 'P1', 'Pin', 'PN-1')"
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE project_basic_information_records (
                record_id VARCHAR(64) PRIMARY KEY,
                project_id VARCHAR(64) NOT NULL,
                status VARCHAR(32) NOT NULL,
                version INTEGER NOT NULL,
                values_json TEXT NOT NULL,
                source_signature_json TEXT NOT NULL,
                created_at VARCHAR(64) NOT NULL,
                updated_at VARCHAR(64) NOT NULL,
                confirmed_at VARCHAR(64),
                confirmed_by VARCHAR(255)
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE intake_cases (
                case_id VARCHAR(64) PRIMARY KEY,
                package_id VARCHAR(64) NOT NULL,
                selected_form_asset_id VARCHAR(64),
                status VARCHAR(64) NOT NULL,
                confirmed_project_id VARCHAR(64),
                created_at VARCHAR(64),
                updated_at VARCHAR(64),
                reviewer_notes TEXT
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE intake_drafts (
                draft_id VARCHAR(64) PRIMARY KEY,
                case_id VARCHAR(64) NOT NULL,
                parsed_fields_json TEXT NOT NULL,
                sample_rows_json TEXT,
                requested_testing_json TEXT,
                field_confidence_json TEXT,
                parser_warnings_json TEXT,
                manual_overrides_json TEXT,
                updated_at VARCHAR(64)
            )
            """
        )
        connection.exec_driver_sql(
            "INSERT INTO intake_cases (case_id, package_id, status, confirmed_project_id) "
            "VALUES ('C1', 'PKG1', 'confirmed', 'P1')"
        )
        parsed_fields = json.dumps(
            {
                "samples": [
                    {"product_name": "Socket", "lubricant": "Yes"},
                    {"product_name": "Pin", "lubricant": "No"},
                ]
            }
        )
        connection.exec_driver_sql(
            "INSERT INTO intake_drafts (draft_id, case_id, parsed_fields_json) "
            "VALUES ('D1', 'C1', ?)",
            (parsed_fields,),
        )
        connection.exec_driver_sql(
            """
            INSERT INTO project_basic_information_records (
                record_id, project_id, status, version, values_json,
                source_signature_json, created_at, updated_at
            ) VALUES (
                'BI-1', 'P1', 'confirmed', 1, '{}', '{}', 'now', 'now'
            )
            """
        )

    init_db(engine)
    init_db(engine)

    sample_columns = {
        column["name"] for column in inspect(engine).get_columns("sample_infos")
    }
    basic_columns = {
        column["name"]
        for column in inspect(engine).get_columns("project_basic_information_records")
    }
    assert {"lubricant", "row_index", "source_form_id"} <= sample_columns
    assert "sample_rows_json" in basic_columns
    with engine.connect() as connection:
        rows = connection.exec_driver_sql(
            "SELECT sample_id, row_index, lubricant FROM sample_infos ORDER BY row_index"
        ).all()
        sample_rows_json = connection.exec_driver_sql(
            "SELECT sample_rows_json FROM project_basic_information_records "
            "WHERE record_id = 'BI-1'"
        ).scalar_one()
    assert rows == [("S2", 0, "Yes"), ("S1", 1, "No")]
    sample_rows = json.loads(sample_rows_json)
    assert [row["product_name"] for row in sample_rows] == ["Socket", "Pin"]
    assert [row["lubricant"] for row in sample_rows] == ["Yes", "No"]


def _record(
    record_id: str,
    *,
    status: str,
    version: int,
    values: dict[str, str],
    updated_at: str = "2026-06-20T09:00:00+00:00",
    sample_rows: tuple[ProjectBasicInformationSampleRow, ...] = tuple(),
) -> ProjectBasicInformationRecord:
    return ProjectBasicInformationRecord(
        record_id=record_id,
        project_id="P1",
        status=status,
        version=version,
        values=values,
        source_signature="{}",
        created_at="2026-06-20T09:00:00+00:00",
        updated_at=updated_at,
        confirmed_at=(
            "2026-06-20T09:00:00+00:00" if status == "confirmed" else None
        ),
        confirmed_by="Lab User" if status == "confirmed" else None,
        sample_rows=sample_rows,
    )
