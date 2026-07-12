from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import inspect

from backend.infrastructure.storage.database import (
    create_database_engine,
    init_db,
)
from backend.shared.config import Settings


def test_contact_measurement_plan_schema_registers_six_additive_tables(tmp_path: Path) -> None:
    engine = create_database_engine(
        Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
        )
    )
    try:
        init_db(engine)
        names = set(inspect(engine).get_table_names())
        assert {
            "measurement_plan_roots",
            "measurement_plan_revisions",
            "measurement_plan_target_snapshots",
            "measurement_plan_family_snapshots",
            "measurement_plan_impacts",
            "measurement_plan_audits",
        } <= names
        revision_indexes = {
            index["name"]
            for index in inspect(engine).get_indexes("measurement_plan_revisions")
        }
        assert {
            "uq_measurement_plan_confirmed_per_root",
            "uq_measurement_plan_editable_per_root",
        } <= revision_indexes
    finally:
        engine.dispose()


def test_schema_rejects_existing_partial_authority_table(tmp_path: Path) -> None:
    database_path = tmp_path / "partial.sqlite3"
    raw_engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with raw_engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE TABLE measurement_plan_roots (measurement_plan_root_id TEXT PRIMARY KEY)"
            )
    finally:
        raw_engine.dispose()

    engine = create_database_engine(
        Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=database_path,
        )
    )
    try:
        with pytest.raises(RuntimeError, match="incompatible"):
            init_db(engine)
    finally:
        engine.dispose()


def test_schema_bootstraps_missing_partial_authority_semantic_indexes(
    tmp_path: Path,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
            _insert_confirmed_revision(connection, "revision-1", "root-1", 1)
            schema_before = _non_index_schema(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        indexes = _index_names(recovered_engine, "measurement_plan_revisions")
        assert _PARTIAL_SEMANTIC_INDEX_NAMES <= indexes
        with recovered_engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT COUNT(*) FROM measurement_plan_revisions"
            ).scalar_one() == 1
            assert _non_index_schema(connection) == schema_before
    finally:
        recovered_engine.dispose()


def test_schema_recognizes_exact_alternate_partial_index_names(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX legacy_confirmed_per_root "
                "ON measurement_plan_revisions(measurement_plan_root_id) "
                "WHERE state = 'confirmed'"
            )
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX legacy_editable_per_root "
                "ON measurement_plan_revisions(measurement_plan_root_id) "
                "WHERE state IN ('draft', 'needs_review')"
            )
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        assert _PARTIAL_SEMANTIC_INDEX_NAMES.isdisjoint(
            _index_names(recovered_engine, "measurement_plan_revisions")
        )
    finally:
        recovered_engine.dispose()


def test_schema_bootstrap_is_idempotent_across_independent_engines(
    tmp_path: Path,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
    finally:
        engine.dispose()

    first_engine = create_database_engine(settings)
    second_engine = create_database_engine(settings)
    try:
        init_db(first_engine)
        first_names = _index_names(first_engine, "measurement_plan_revisions")
        init_db(second_engine)
        assert _index_names(second_engine, "measurement_plan_revisions") == first_names
    finally:
        first_engine.dispose()
        second_engine.dispose()


def test_schema_blocks_duplicate_missing_partial_index_before_ddl(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
            _insert_confirmed_revision(connection, "revision-1", "root-1", 1)
            _insert_confirmed_revision(connection, "revision-2", "root-1", 2)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(recovered_engine)
        assert _PARTIAL_SEMANTIC_INDEX_NAMES.isdisjoint(_index_names(
            recovered_engine,
            "measurement_plan_revisions",
        ))
    finally:
        recovered_engine.dispose()


def test_schema_blocks_nullable_authority_identity_before_index_ddl(
    tmp_path: Path,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
            table_sql = connection.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE type='table' "
                "AND name='measurement_plan_revisions'"
            ).scalar_one()
            connection.exec_driver_sql("PRAGMA writable_schema=ON")
            connection.exec_driver_sql(
                "UPDATE sqlite_master SET sql=? WHERE type='table' "
                "AND name='measurement_plan_revisions'",
                (
                    table_sql.replace(
                        "measurement_plan_root_id VARCHAR(64) NOT NULL",
                        "measurement_plan_root_id VARCHAR(64)",
                    ),
                ),
            )
            connection.exec_driver_sql("PRAGMA writable_schema=OFF")
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(recovered_engine)
        assert _PARTIAL_SEMANTIC_INDEX_NAMES.isdisjoint(
            _index_names(recovered_engine, "measurement_plan_revisions")
        )
    finally:
        recovered_engine.dispose()


def test_schema_rolls_back_partial_index_bootstrap_on_ddl_failure(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)

    def fail_second_index(_, __, statement, *___):
        if "CREATE UNIQUE INDEX uq_measurement_plan_editable_per_root" in statement:
            raise RuntimeError("simulated DDL failure")

    event.listen(recovered_engine, "before_cursor_execute", fail_second_index)
    try:
        with pytest.raises(RuntimeError, match="simulated DDL failure"):
            init_db(recovered_engine)
        assert _PARTIAL_SEMANTIC_INDEX_NAMES.isdisjoint(
            _index_names(recovered_engine, "measurement_plan_revisions")
        )
    finally:
        event.remove(recovered_engine, "before_cursor_execute", fail_second_index)
        recovered_engine.dispose()


def test_schema_reports_locked_bootstrap_without_fallback(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            for index_name in _PARTIAL_SEMANTIC_INDEX_NAMES:
                connection.exec_driver_sql(f"DROP INDEX {index_name}")
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


def test_schema_rejects_same_name_partial_index_with_extra_predicate(tmp_path: Path) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "DROP INDEX uq_measurement_plan_confirmed_per_root"
            )
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX uq_measurement_plan_confirmed_per_root "
                "ON measurement_plan_revisions(measurement_plan_root_id) "
                "WHERE state = 'confirmed' AND revision_sequence > 0"
            )
    finally:
        engine.dispose()

    invalid_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(invalid_engine)
    finally:
        invalid_engine.dispose()


def test_schema_rejects_same_token_check_with_changed_boolean_grouping(
    tmp_path: Path,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            sql = connection.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE type='table' "
                "AND name='measurement_plan_target_snapshots'"
            ).scalar_one()
            changed = sql.replace(
                ") OR (source_group_snapshot_id IS NULL",
                ") AND (source_group_snapshot_id IS NULL",
                1,
            )
            connection.exec_driver_sql("PRAGMA writable_schema=ON")
            connection.exec_driver_sql(
                "UPDATE sqlite_master SET sql=? WHERE type='table' "
                "AND name='measurement_plan_target_snapshots'",
                (changed,),
            )
            connection.exec_driver_sql("PRAGMA writable_schema=OFF")
    finally:
        engine.dispose()

    invalid_engine = create_database_engine(settings)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(invalid_engine)
    finally:
        invalid_engine.dispose()


def _fresh_authority_database(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "authority.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return engine, settings


def _index_names(engine, table_name: str) -> set[str]:
    with engine.connect() as connection:
        return {
            str(row[1])
            for row in connection.exec_driver_sql(f"PRAGMA index_list({table_name})").all()
        }


def _non_index_schema(connection) -> dict[str, str]:
    return {
        str(row[0]): str(row[1])
        for row in connection.exec_driver_sql(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type='table' AND name LIKE 'measurement_plan_%'"
        ).all()
    }


def _insert_confirmed_revision(connection, revision_id: str, root_id: str, sequence: int) -> None:
    connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    connection.exec_driver_sql(
        "INSERT INTO measurement_plan_revisions ("
        "measurement_plan_revision_id, measurement_plan_root_id, revision_sequence, "
        "state, revision_fingerprint, base_confirmed_matrix_id, base_matrix_revision, "
        "matrix_binding_fingerprint, created_by, created_at, updated_at"
        ") VALUES (?, ?, ?, 'confirmed', 'fingerprint', 'matrix-1', 1, 'binding', "
        "'operator', '2026-07-13T00:00:00Z', '2026-07-13T00:00:00Z')",
        (revision_id, root_id, sequence),
    )


_PARTIAL_SEMANTIC_INDEX_NAMES = {
    "uq_measurement_plan_confirmed_per_root",
    "uq_measurement_plan_editable_per_root",
}
