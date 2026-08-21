from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from backend.infrastructure.storage import standard_record_method_sync_schema_migration as schema
from backend.infrastructure.storage.standard_record_method_sync_schema_migration import (
    StandardRecordMethodSyncSchemaError,
    migrate_standard_record_method_sync_schema,
)


def test_migration_adds_both_nullable_columns_and_is_idempotent(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.sqlite3'}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE external_resources (resource_id VARCHAR(64) PRIMARY KEY)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE project_matrix_draft_records "
            "(project_matrix_draft_id VARCHAR(64) PRIMARY KEY)"
        )

    migrate_standard_record_method_sync_schema(engine)
    migrate_standard_record_method_sync_schema(engine)

    with engine.connect() as connection:
        external = {
            row[1]: (row[2], row[3], row[4], row[5])
            for row in connection.exec_driver_sql(
                "PRAGMA table_info(external_resources)"
            ).all()
        }
        matrix = {
            row[1]: (row[2], row[3], row[4], row[5])
            for row in connection.exec_driver_sql(
                "PRAGMA table_info(project_matrix_draft_records)"
            ).all()
        }

    assert external["worksheet_name"] == ("VARCHAR(31)", 0, None, 0)
    assert matrix["method_sync_context_json"] == ("TEXT", 0, None, 0)


def test_migration_completes_one_column_partial_state(tmp_path) -> None:
    engine = _legacy_engine(tmp_path, external_column="VARCHAR(31)")

    migrate_standard_record_method_sync_schema(engine)

    assert _column(engine, "external_resources", "worksheet_name") == (
        "VARCHAR(31)", 0, None, 0
    )
    assert _column(engine, "project_matrix_draft_records", "method_sync_context_json") == (
        "TEXT", 0, None, 0
    )


def test_malformed_existing_column_fails_before_any_ddl(tmp_path) -> None:
    engine = _legacy_engine(tmp_path, external_column="INTEGER")

    with pytest.raises(StandardRecordMethodSyncSchemaError, match="authority_corrupt"):
        migrate_standard_record_method_sync_schema(engine)

    assert _column(engine, "external_resources", "worksheet_name") == (
        "INTEGER", 0, None, 0
    )
    assert _column(engine, "project_matrix_draft_records", "method_sync_context_json") is None


def test_final_verification_failure_rolls_back_both_alters(tmp_path, monkeypatch) -> None:
    engine = _legacy_engine(tmp_path)
    original = schema._column_shape
    calls = 0

    def fail_final_verify(connection, table, column):
        nonlocal calls
        calls += 1
        result = original(connection, table, column)
        if calls >= 5 and table == "external_resources":
            return ("BROKEN", 0, None, 0)
        return result

    monkeypatch.setattr(schema, "_column_shape", fail_final_verify)
    with pytest.raises(StandardRecordMethodSyncSchemaError, match="authority_corrupt"):
        migrate_standard_record_method_sync_schema(engine)

    assert _column(engine, "external_resources", "worksheet_name") is None
    assert _column(engine, "project_matrix_draft_records", "method_sync_context_json") is None


def test_locked_writer_fails_closed_then_recovers(tmp_path) -> None:
    engine = _legacy_engine(tmp_path, timeout=0.05)
    lock = engine.connect()
    lock.exec_driver_sql("BEGIN IMMEDIATE")
    try:
        with pytest.raises(StandardRecordMethodSyncSchemaError, match="locked"):
            migrate_standard_record_method_sync_schema(engine)
        assert _column(engine, "external_resources", "worksheet_name") is None
    finally:
        lock.rollback()
        lock.close()

    migrate_standard_record_method_sync_schema(engine)
    assert _column(engine, "external_resources", "worksheet_name") is not None


def _legacy_engine(tmp_path, *, external_column=None, timeout=5.0):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'compat.sqlite3'}",
        future=True,
        connect_args={"timeout": timeout},
    )
    suffix = f", worksheet_name {external_column}" if external_column else ""
    with engine.begin() as connection:
        connection.exec_driver_sql(
            f"CREATE TABLE external_resources (resource_id VARCHAR(64) PRIMARY KEY{suffix})"
        )
        connection.exec_driver_sql(
            "CREATE TABLE project_matrix_draft_records "
            "(project_matrix_draft_id VARCHAR(64) PRIMARY KEY)"
        )
    return engine


def _column(engine, table, column):
    with engine.connect() as connection:
        for row in connection.exec_driver_sql(f"PRAGMA table_info({table})").all():
            if row[1] == column:
                return (row[2], row[3], row[4], row[5])
    return None
