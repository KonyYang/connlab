"""Disposable TASK_361G schema-CHECK compatibility startup coverage."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import event, inspect
from sqlalchemy.exc import IntegrityError

from backend.api.main import app
from backend.infrastructure.storage.database import create_database_engine, init_db
from backend.shared.config import Settings
from tests.integration.test_confirmed_matrix_test_record_preview_api import (
    _client as _preview_client,
)
from tests.integration.test_confirmed_matrix_test_record_preview_api import (
    _seed_empty_active_confirmed_snapshot,
    _seed_project as _seed_preview_project,
)
from tests.integration.test_matrix_editor_session_api import _client as _session_client
from tests.integration.test_matrix_editor_session_api import _seed_project as _seed_session_project


def test_missing_authority_checks_bootstrap_canonical_guards(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        assert _trigger_names(recovered_engine) == _CANONICAL_TRIGGER_NAMES
    finally:
        recovered_engine.dispose()


def test_exact_alternate_check_names_need_no_compatibility_guards(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _rename_authority_checks(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        assert _trigger_names(recovered_engine) == set()
    finally:
        recovered_engine.dispose()


def test_missing_target_key_check_does_not_match_impact_subject_check(
    tmp_path: Path,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _rebuild_without_checks(
                connection,
                "measurement_plan_target_snapshots",
                ("ck_measurement_plan_target_key_shape",),
            )
            impact_checks = {
                str(item.get("name"))
                for item in inspect(connection).get_check_constraints(
                    "measurement_plan_impacts"
                )
            }
            assert "ck_measurement_plan_impact_subject_shape" in impact_checks
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        assert _trigger_names(recovered_engine) == {
            "trg_cmp_target_checks_insert_v1",
            "trg_cmp_target_checks_update_v1",
        }
    finally:
        recovered_engine.dispose()


@pytest.mark.parametrize("kind", ("target", "impact"))
def test_invalid_legacy_row_blocks_before_trigger_or_index_ddl(
    tmp_path: Path,
    kind: str,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
            connection.exec_driver_sql("DROP INDEX uq_measurement_plan_confirmed_per_root")
            connection.exec_driver_sql("DROP INDEX uq_measurement_plan_editable_per_root")
            if kind == "target":
                _insert_target(connection, "target-invalid", "not-a-target-key")
            else:
                _insert_impact(connection, "impact-invalid", "not-an-impact-key")
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(recovered_engine)
        assert _trigger_names(recovered_engine) == set()
        assert _partial_index_names(recovered_engine) == set()
    finally:
        recovered_engine.dispose()


def test_canonical_guards_reject_invalid_insert_and_relevant_update(
    tmp_path: Path,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        with pytest.raises(IntegrityError, match="target CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                _insert_target(connection, "target-invalid", "not-a-target-key")
        with recovered_engine.begin() as connection:
            _insert_target(connection, "target-valid", "cmp-target:v1|valid")
        with pytest.raises(IntegrityError, match="target CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                connection.exec_driver_sql(
                    "UPDATE measurement_plan_target_snapshots "
                    "SET stable_target_key='not-a-target-key' "
                    "WHERE measurement_plan_target_snapshot_id='target-valid'"
                )
        with pytest.raises(IntegrityError, match="impact CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                _insert_impact(connection, "impact-invalid", "not-an-impact-key")
    finally:
        recovered_engine.dispose()


def test_guard_bootstrap_rolls_back_when_second_trigger_ddl_fails(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)

    def fail_second_trigger(_, __, statement, *___):
        if statement.startswith("CREATE TRIGGER trg_cmp_target_checks_update_v1"):
            raise RuntimeError("simulated trigger DDL failure")

    event.listen(recovered_engine, "before_cursor_execute", fail_second_trigger)
    try:
        with pytest.raises(RuntimeError, match="simulated trigger DDL failure"):
            init_db(recovered_engine)
        assert _trigger_names(recovered_engine) == set()
    finally:
        event.remove(recovered_engine, "before_cursor_execute", fail_second_trigger)
        recovered_engine.dispose()


def test_guard_and_index_bootstrap_share_one_rollback_transaction(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
            connection.exec_driver_sql("DROP INDEX uq_measurement_plan_confirmed_per_root")
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)

    def fail_index_after_guards(_, __, statement, *___):
        if statement.startswith("CREATE UNIQUE INDEX uq_measurement_plan_confirmed_per_root"):
            raise RuntimeError("simulated shared bootstrap failure")

    event.listen(recovered_engine, "before_cursor_execute", fail_index_after_guards)
    try:
        with pytest.raises(RuntimeError, match="simulated shared bootstrap failure"):
            init_db(recovered_engine)
        assert _trigger_names(recovered_engine) == set()
        assert _partial_index_names(recovered_engine) == {
            "uq_measurement_plan_editable_per_root"
        }
    finally:
        event.remove(recovered_engine, "before_cursor_execute", fail_index_after_guards)
        recovered_engine.dispose()


def test_guard_bootstrap_is_idempotent(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    first_engine = create_database_engine(settings)
    second_engine = create_database_engine(settings)
    try:
        init_db(first_engine)
        first_triggers = _trigger_names(first_engine)
        init_db(second_engine)
        assert _trigger_names(second_engine) == first_triggers
    finally:
        first_engine.dispose()
        second_engine.dispose()


def test_same_name_wrong_guard_is_authority_corrupt(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
            connection.exec_driver_sql(
                "CREATE TRIGGER trg_cmp_target_checks_insert_v1 "
                "BEFORE INSERT ON measurement_plan_target_snapshots "
                "BEGIN SELECT 1; END"
            )
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(recovered_engine)
    finally:
        recovered_engine.dispose()


def test_check_guard_bootstrap_reports_locked_writer(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    lock_engine = create_database_engine(settings, connect_args={"timeout": 0})
    blocked_engine = create_database_engine(settings, connect_args={"timeout": 0})
    try:
        with lock_engine.connect() as lock_connection:
            lock_connection.exec_driver_sql("BEGIN IMMEDIATE")
            with pytest.raises(RuntimeError, match="locked"):
                init_db(blocked_engine)
            lock_connection.rollback()
    finally:
        lock_engine.dispose()
        blocked_engine.dispose()


def test_missing_checks_no_longer_mask_matrix_session_get(tmp_path: Path) -> None:
    client, engine, _ = _session_client(tmp_path)
    try:
        _seed_session_project("P1", tmp_path)
        with engine.begin() as connection:
            _remove_authority_checks(connection)
        init_db(engine)
        assert client.get("/api/projects/P1/matrix-editor/session").status_code == 200
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_missing_checks_no_longer_mask_read_only_test_record_preview(tmp_path: Path) -> None:
    client, engine, _ = _preview_client(tmp_path)
    try:
        _seed_preview_project("P1", tmp_path)
        _seed_empty_active_confirmed_snapshot("P1", tmp_path)
        with engine.begin() as connection:
            _remove_authority_checks(connection)
        init_db(engine)
        response = client.get("/api/projects/P1/confirmed-matrix/test-record-preview")
        assert response.status_code == 200
        assert response.json()["preview_status"] == "empty"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _fresh_authority_database(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "authority-checks.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return engine, settings


def _remove_authority_checks(connection) -> None:
    _rebuild_without_checks(
        connection,
        "measurement_plan_target_snapshots",
        (
            "ck_measurement_plan_group_anchor_xor",
            "ck_measurement_plan_row_anchor_xor",
            "ck_measurement_plan_target_key_shape",
        ),
    )
    _rebuild_without_checks(
        connection,
        "measurement_plan_impacts",
        (
            "ck_measurement_plan_impact_subject_shape",
            "ck_measurement_plan_impact_identity_shape",
        ),
    )


def _rename_authority_checks(connection) -> None:
    for table_name, check_names in (
        (
            "measurement_plan_target_snapshots",
            (
                "ck_measurement_plan_group_anchor_xor",
                "ck_measurement_plan_row_anchor_xor",
                "ck_measurement_plan_target_key_shape",
            ),
        ),
        (
            "measurement_plan_impacts",
            (
                "ck_measurement_plan_impact_subject_shape",
                "ck_measurement_plan_impact_identity_shape",
            ),
        ),
    ):
        _rebuild_table_sql(
            connection,
            table_name,
            tuple((name, f"legacy_{name}") for name in check_names),
        )


def _rebuild_without_checks(connection, table_name: str, check_names: tuple[str, ...]) -> None:
    replacements = tuple((f"\tCONSTRAINT {name} CHECK ", "") for name in check_names)
    _rebuild_table_sql(connection, table_name, replacements, remove_check_lines=True)


def _rebuild_table_sql(
    connection,
    table_name: str,
    replacements: tuple[tuple[str, str], ...],
    *,
    remove_check_lines: bool = False,
) -> None:
    replacement_name = f"{table_name}_legacy"
    table_sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).scalar_one()
    replacement_sql = table_sql.replace(
        f"CREATE TABLE {table_name} (",
        f"CREATE TABLE {replacement_name} (",
        1,
    )
    for old, new in replacements:
        if remove_check_lines:
            line_start = replacement_sql.index(old)
            line_end = replacement_sql.index(", \n", line_start) + len(", \n")
            replacement_sql = replacement_sql[:line_start] + replacement_sql[line_end:]
        else:
            replacement_sql = replacement_sql.replace(old, new, 1)
    connection.exec_driver_sql(replacement_sql)
    connection.exec_driver_sql(
        f"INSERT INTO {replacement_name} SELECT * FROM {table_name}"
    )
    connection.exec_driver_sql(f"DROP TABLE {table_name}")
    connection.exec_driver_sql(f"ALTER TABLE {replacement_name} RENAME TO {table_name}")


def _trigger_names(engine) -> set[str]:
    with engine.connect() as connection:
        return {
            str(row[0])
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            ).all()
        }


def _partial_index_names(engine) -> set[str]:
    with engine.connect() as connection:
        return {
            str(row[1])
            for row in connection.exec_driver_sql(
                "PRAGMA index_list(measurement_plan_revisions)"
            ).all()
            if str(row[1]) in {
                "uq_measurement_plan_confirmed_per_root",
                "uq_measurement_plan_editable_per_root",
            }
        }


def _insert_target(
    connection,
    target_id: str,
    stable_target_key: str,
    *,
    source_group_snapshot_id: str | None = "group-source",
    manual_group_anchor_id: str | None = None,
    source_row_snapshot_id: str | None = "row-source",
    manual_row_anchor_id: str | None = None,
) -> None:
    connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    connection.exec_driver_sql(
        "INSERT INTO measurement_plan_target_snapshots ("
        "measurement_plan_target_snapshot_id, measurement_plan_revision_id, stable_target_key, "
        "source_group_snapshot_id, manual_group_anchor_id, source_row_snapshot_id, "
        "manual_row_anchor_id, confirmed_matrix_id, confirmed_group_id, confirmed_row_id, "
        "matrix_revision, step_sequence, step_suffix_note, group_label, test_item, contact_kind, "
        "sample_quantity_expression, eligible, included, is_override, coverage_state, impact_status, "
        "binding_evidence_fingerprint, readings_per_sample"
        ") VALUES (?, 'revision-1', ?, ?, ?, ?, ?, 'matrix-1', "
        "'group-1', 'row-1', 1, 1, '', 'Group 1', 'LLCR', 'llcr', '1', 1, 1, 0, "
        "'included', 'unchanged', 'binding', 1)",
        (
            target_id,
            stable_target_key,
            source_group_snapshot_id,
            manual_group_anchor_id,
            source_row_snapshot_id,
            manual_row_anchor_id,
        ),
    )


def _insert_impact(
    connection,
    impact_id: str,
    impact_identity_key: str,
    *,
    impact_subject_key: str = "cmp-target:v1|target",
) -> None:
    connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    connection.exec_driver_sql(
        "INSERT INTO measurement_plan_impacts ("
        "measurement_plan_impact_id, measurement_plan_root_id, editable_revision_id, "
        "stable_target_key, impact_subject_key, impact_identity_key, category, severity, "
        "before_evidence_fingerprint, after_evidence_fingerprint, resolution_state, created_at"
        ") VALUES (?, 'root-1', 'revision-1', 'cmp-target:v1|target', "
        "?, ?, 'review', 'warning', 'before', 'after', 'open', "
        "'2026-07-13T00:00:00Z')",
        (impact_id, impact_subject_key, impact_identity_key),
    )


_CANONICAL_TRIGGER_NAMES = {
    "trg_cmp_target_checks_insert_v1",
    "trg_cmp_target_checks_update_v1",
    "trg_cmp_impact_checks_insert_v1",
    "trg_cmp_impact_checks_update_v1",
}
