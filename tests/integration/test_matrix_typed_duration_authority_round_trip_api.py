from pathlib import Path
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, inspect

from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.matrix_duration_authority_schema import (
    MATRIX_DURATION_AUTHORITY_TABLES,
    MatrixDurationAuthoritySchemaError,
)
from backend.infrastructure.storage.database import Base
from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixImportCommand,
    SourceMatrixImportPersistenceService,
)
from backend.infrastructure.storage.repositories import SourceMatrixImportRepository
from tests.integration.test_confirmed_matrix_authority_api import (
    _client,
    _seed_project,
)


def _engine(path: Path):
    return create_engine(f"sqlite:///{path.as_posix()}", future=True)


def test_init_db_creates_all_duration_authority_tables_idempotently(
    tmp_path: Path,
) -> None:
    engine = _engine(tmp_path / "duration.sqlite3")

    init_db(engine)
    first_tables = set(inspect(engine).get_table_names())
    init_db(engine)
    second_tables = set(inspect(engine).get_table_names())

    assert set(MATRIX_DURATION_AUTHORITY_TABLES).issubset(first_tables)
    assert second_tables == first_tables


@pytest.mark.parametrize("existing_name", MATRIX_DURATION_AUTHORITY_TABLES)
def test_partial_duration_authority_shape_fails_before_missing_ddl(
    tmp_path: Path,
    existing_name: str,
) -> None:
    engine = _engine(tmp_path / f"{existing_name}.sqlite3")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            f'CREATE TABLE "{existing_name}" (placeholder TEXT NOT NULL)'
        )
    before = set(inspect(engine).get_table_names())

    with pytest.raises(
        MatrixDurationAuthoritySchemaError,
        match="authority_corrupt",
    ):
        init_db(engine)

    after = set(inspect(engine).get_table_names())
    assert after.intersection(MATRIX_DURATION_AUTHORITY_TABLES) == {
        existing_name
    }
    assert before.issubset(after)


def test_existing_wrong_named_check_fails_closed_without_schema_mutation(
    tmp_path: Path,
) -> None:
    engine = _engine(tmp_path / "wrong-check.sqlite3")
    with engine.begin() as connection:
        for name in MATRIX_DURATION_AUTHORITY_TABLES:
            Base.metadata.tables[name].create(connection)
        table_name = "project_matrix_draft_duration_authorities"
        sql = connection.exec_driver_sql(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name = ?",
            (table_name,),
        ).scalar_one()
        connection.exec_driver_sql(f'DROP TABLE "{table_name}"')
        connection.exec_driver_sql(
            sql.replace(
                "ck_draft_duration_step_positive",
                "ck_draft_duration_step_positive_wrong",
            )
        )
    before = _schema_objects(engine)

    with pytest.raises(MatrixDurationAuthoritySchemaError, match="authority_corrupt"):
        init_db(engine)

    assert _schema_objects(engine) == before


def test_structured_duration_authority_round_trips_source_draft_and_confirmed_api(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        with session_factory() as session:
            source_import_id = SourceMatrixImportPersistenceService(
                store=SourceMatrixImportRepository(session)
            ).persist_from_draft(
                PersistSourceMatrixImportCommand(
                    project_id="P1",
                    draft_id="ptpd-duration",
                    source_document_path="C:/disposable/spec.docx",
                    source_document_name="spec.docx",
                    source_format=".docx",
                    source_asset_id=None,
                    source_case_id=None,
                    source_draft_id=None,
                    payload=_source_payload(),
                    created_at="2026-07-24T08:00:00+00:00",
                )
            )
            session.commit()

        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={
                "source_import_id": source_import_id,
                "selected_group_keys": ["g1"],
            },
        )
        assert created.status_code == 201
        draft = created.json()
        authority = draft["duration_authorities"]
        assert len(authority) == 1
        assert Decimal(authority[0]["duration_value"]) == Decimal("2")
        assert Decimal(authority[0]["normalized_hours"]) == Decimal("48")
        assert authority[0]["step_suffix_note"] == ""

        draft_id = draft["record"]["project_matrix_draft_id"]
        reloaded = client.get(f"/api/projects/P1/matrix-drafts/{draft_id}")
        assert reloaded.status_code == 200
        assert reloaded.json()["duration_authorities"] == authority

        save_payload = _draft_save_payload(draft)
        omitted = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json=save_payload,
        )
        assert omitted.status_code == 200
        assert omitted.json()["duration_authorities"] == authority

        cleared = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={**save_payload, "duration_authorities": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["duration_authorities"] == []

        restored = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={
                **save_payload,
                "duration_authorities": [
                    {
                        "draft_duration_authority_id": authority[0][
                            "duration_authority_id"
                        ],
                        "draft_group_id": authority[0]["group_id"],
                        "draft_row_id": authority[0]["row_id"],
                        "step_sequence": 1,
                        "step_suffix_note": "",
                        "duration_value": "2",
                        "duration_unit": "days",
                        "source_kind": "import_structured",
                        "source_field": "duration_authorities[0]",
                        "source_import_id": source_import_id,
                        "source_fingerprint": authority[0]["source_fingerprint"],
                        "lineage_fingerprint": authority[0]["lineage_fingerprint"],
                        "authority_revision": "1",
                    }
                ],
            },
        )
        assert restored.status_code == 200
        assert len(restored.json()["duration_authorities"]) == 1

        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201
        confirmed_authority = confirmed.json()["duration_authorities"]
        assert len(confirmed_authority) == 1
        assert Decimal(confirmed_authority[0]["duration_value"]) == Decimal("2")
        assert Decimal(confirmed_authority[0]["normalized_hours"]) == Decimal("48")
    finally:
        from backend.api.main import app

        app.dependency_overrides.clear()
        engine.dispose()


def _source_payload() -> dict[str, object]:
    return {
        "groups": [
            {
                "group_key": "g1",
                "group_label": "G1",
                "sample_quantity_expression": "5",
            }
        ],
        "rows": [
            {
                "source_row_index": 3,
                "test_item": "Long-term high temperature zone load",
                "source_section": "6.1",
                "group_tokens": {"G1": "1"},
                "is_sample_row": False,
                "duration_authorities": [
                    {
                        "owning_group_key": "g1",
                        "step_sequence": 1,
                        "step_suffix_note": "",
                        "duration_value": 2,
                        "duration_unit": "days",
                        "source_field": "duration_authorities[0]",
                        "source_identity": {"group_key": "g1"},
                    }
                ],
            },
            {
                "source_row_index": 4,
                "test_item": "Samples Quantity (PCS)",
                "group_tokens": {"G1": "5"},
                "is_sample_row": True,
            },
        ],
        "warnings": [],
        "blockers": [],
        "selected_group_keys_at_import": ["g1"],
    }


def _schema_objects(engine) -> tuple[tuple[str, str], ...]:
    with engine.connect() as connection:
        return tuple(
            connection.exec_driver_sql(
                "SELECT type, name FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
            ).all()
        )


def _draft_save_payload(draft: dict[str, object]) -> dict[str, object]:
    groups = draft["groups"]
    rows = draft["rows"]
    cells = draft["cells"]
    assert isinstance(groups, list) and isinstance(rows, list) and isinstance(cells, list)
    return {
        "groups": groups,
        "rows": rows,
        "cells": [
            {
                "draft_row_id": item["draft_row_id"],
                "draft_group_id": item["draft_group_id"],
                "cell_value": item["cell_value"],
            }
            for item in cells
        ],
    }
