"""Disposable startup probes for TASK_361F schema compatibility bootstrap."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.api.main import app
from backend.infrastructure.storage.contact_measurement_plan_authority_schema_migration import (
    migrate_contact_measurement_plan_authority_schema,
)
from backend.infrastructure.storage.database import create_database_engine, init_db
from backend.shared.config import Settings
from tests.integration.test_matrix_editor_session_api import _client, _seed_project


def test_missing_authority_indexes_no_longer_mask_existing_matrix_routes(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "DROP INDEX uq_measurement_plan_confirmed_per_root"
            )
            connection.exec_driver_sql(
                "DROP INDEX uq_measurement_plan_editable_per_root"
            )

        init_db(engine)

        assert client.get("/api/projects/P1/matrix-editor/session").status_code == 200
        assert client.request(
            "DELETE",
            "/api/projects/P1/matrix-editor/session/draft",
            json={"expected_editor_draft_id": "missing-draft"},
        ).status_code != 500
        assert client.post(
            "/api/projects/P1/matrix-editor/test-record-draft/generate",
            json={"source": "saved_draft", "groups": [], "rows": []},
        ).status_code == 422
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_all_four_missing_semantic_indexes_bootstrap_full_pair_constraints(
    tmp_path: Path,
) -> None:
    engine, settings = _legacy_authority_engine(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_all_semantic_indexes(connection)
            _insert_target(connection, "target-1", "revision-1", "target-1")
            _insert_impact(connection, "impact-1", "revision-1", "impact-1")
            schema_before = _non_index_schema(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        assert _all_canonical_indexes(recovered_engine)
        with recovered_engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT COUNT(*) FROM measurement_plan_target_snapshots"
            ).scalar_one() == 1
            assert connection.exec_driver_sql(
                "SELECT COUNT(*) FROM measurement_plan_impacts"
            ).scalar_one() == 1
            assert _non_index_schema(connection) == schema_before
    finally:
        recovered_engine.dispose()


@pytest.mark.parametrize("kind", ("target", "impact"))
def test_missing_full_pair_duplicate_blocks_all_canonical_ddl(
    tmp_path: Path,
    kind: str,
) -> None:
    engine, settings = _legacy_authority_engine(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_all_semantic_indexes(connection)
            if kind == "target":
                _insert_target(connection, "target-1", "revision-1", "same")
                _insert_target(connection, "target-2", "revision-1", "same")
            else:
                _insert_impact(connection, "impact-1", "revision-1", "same")
                _insert_impact(connection, "impact-2", "revision-1", "same")
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            migrate_contact_measurement_plan_authority_schema(recovered_engine)
        assert _canonical_index_names(recovered_engine) == set()
    finally:
        recovered_engine.dispose()


@pytest.mark.parametrize(
    ("table_name", "column_name", "kind"),
    (
        ("measurement_plan_target_snapshots", "stable_target_key", "target"),
        ("measurement_plan_impacts", "impact_identity_key", "impact"),
    ),
)
def test_missing_full_pair_null_blocks_all_canonical_ddl(
    tmp_path: Path,
    table_name: str,
    column_name: str,
    kind: str,
) -> None:
    engine, settings = _legacy_authority_engine(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_all_semantic_indexes(connection)
            _make_column_nullable(connection, table_name, column_name)
    finally:
        engine.dispose()

    nullable_engine = create_database_engine(settings)
    try:
        with nullable_engine.begin() as connection:
            if kind == "target":
                _insert_target(connection, "target-null", "revision-1", None)
            else:
                _insert_impact(connection, "impact-null", "revision-1", None)
    finally:
        nullable_engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            migrate_contact_measurement_plan_authority_schema(recovered_engine)
        assert _canonical_index_names(recovered_engine) == set()
    finally:
        recovered_engine.dispose()


def _legacy_authority_engine(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "authority-legacy.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return engine, settings


def _remove_all_semantic_indexes(connection) -> None:
    connection.exec_driver_sql("DROP INDEX uq_measurement_plan_confirmed_per_root")
    connection.exec_driver_sql("DROP INDEX uq_measurement_plan_editable_per_root")
    _rebuild_without_unique_constraint(
        connection,
        "measurement_plan_target_snapshots",
        "uq_measurement_plan_target_key",
        "measurement_plan_revision_id, stable_target_key",
    )
    _rebuild_without_unique_constraint(
        connection,
        "measurement_plan_impacts",
        "uq_measurement_plan_impact_identity",
        "editable_revision_id, impact_identity_key",
    )


def _rebuild_without_unique_constraint(
    connection,
    table_name: str,
    constraint_name: str,
    columns: str,
) -> None:
    replacement_name = f"{table_name}_legacy"
    table_sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).scalar_one()
    constraint = f"\tCONSTRAINT {constraint_name} UNIQUE ({columns}), \n"
    replacement_sql = table_sql.replace(
        f"CREATE TABLE {table_name} (",
        f"CREATE TABLE {replacement_name} (",
        1,
    ).replace(constraint, "")
    assert replacement_sql != table_sql
    connection.exec_driver_sql(replacement_sql)
    connection.exec_driver_sql(
        f"INSERT INTO {replacement_name} SELECT * FROM {table_name}"
    )
    connection.exec_driver_sql(f"DROP TABLE {table_name}")
    connection.exec_driver_sql(f"ALTER TABLE {replacement_name} RENAME TO {table_name}")


def _insert_target(connection, target_id: str, revision_id: str, key_suffix: str | None) -> None:
    connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    connection.exec_driver_sql(
        "INSERT INTO measurement_plan_target_snapshots ("
        "measurement_plan_target_snapshot_id, measurement_plan_revision_id, stable_target_key, "
        "source_group_snapshot_id, manual_group_anchor_id, source_row_snapshot_id, "
        "manual_row_anchor_id, confirmed_matrix_id, confirmed_group_id, confirmed_row_id, "
        "matrix_revision, step_sequence, step_suffix_note, group_label, test_item, contact_kind, "
        "sample_quantity_expression, eligible, included, is_override, coverage_state, impact_status, "
        "binding_evidence_fingerprint, readings_per_sample"
        ") VALUES (?, ?, ?, 'group-source', NULL, 'row-source', NULL, 'matrix-1', "
        "'group-1', 'row-1', 1, 1, '', 'Group 1', 'LLCR', 'llcr', '1', 1, 1, 0, "
        "'included', 'unchanged', 'binding', 1)",
        (target_id, revision_id, None if key_suffix is None else f"cmp-target:v1|{key_suffix}"),
    )


def _insert_impact(connection, impact_id: str, revision_id: str, key_suffix: str | None) -> None:
    connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    connection.exec_driver_sql(
        "INSERT INTO measurement_plan_impacts ("
        "measurement_plan_impact_id, measurement_plan_root_id, editable_revision_id, "
        "stable_target_key, impact_subject_key, impact_identity_key, category, severity, "
        "before_evidence_fingerprint, after_evidence_fingerprint, resolution_state, created_at"
        ") VALUES (?, 'root-1', ?, 'cmp-target:v1|target', 'cmp-target:v1|target', ?, "
        "'review', 'warning', 'before', 'after', 'open', '2026-07-13T00:00:00Z')",
        (impact_id, revision_id, None if key_suffix is None else f"cmp-impact:v1|{key_suffix}"),
    )


def _make_column_nullable(connection, table_name: str, column_name: str) -> None:
    _replace_table_sql(
        connection,
        table_name,
        f"{column_name} TEXT NOT NULL",
        f"{column_name} TEXT",
    )


def _replace_table_sql(connection, table_name: str, old: str, new: str) -> None:
    table_sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).scalar_one()
    updated_sql = table_sql.replace(old, new, 1)
    assert updated_sql != table_sql
    connection.exec_driver_sql("PRAGMA writable_schema=ON")
    connection.exec_driver_sql(
        "UPDATE sqlite_master SET sql=? WHERE type='table' AND name=?",
        (updated_sql, table_name),
    )
    connection.exec_driver_sql("PRAGMA writable_schema=OFF")


def _all_canonical_indexes(engine) -> bool:
    return _canonical_index_names(engine) == _ALL_CANONICAL_INDEX_NAMES


def _canonical_index_names(engine) -> set[str]:
    return {
        index_name
        for table_name, index_names in _CANONICAL_INDEXES_BY_TABLE.items()
        for index_name in index_names
        if index_name in _index_names(engine, table_name)
    }


def _index_names(engine, table_name: str) -> set[str]:
    with engine.connect() as connection:
        return {
            str(row[1])
            for row in connection.exec_driver_sql(
                f"PRAGMA index_list({table_name})"
            ).all()
        }


_CANONICAL_INDEXES_BY_TABLE = {
    "measurement_plan_revisions": {
        "uq_measurement_plan_confirmed_per_root",
        "uq_measurement_plan_editable_per_root",
    },
    "measurement_plan_target_snapshots": {"uq_measurement_plan_target_key"},
    "measurement_plan_impacts": {"uq_measurement_plan_impact_identity"},
}

_ALL_CANONICAL_INDEX_NAMES = {
    index_name
    for index_names in _CANONICAL_INDEXES_BY_TABLE.values()
    for index_name in index_names
}

def _non_index_schema(connection) -> dict[str, str]:
    return {
        str(row[0]): str(row[1])
        for row in connection.exec_driver_sql(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type='table' AND name LIKE 'measurement_plan_%'"
        ).all()
    }
