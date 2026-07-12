from pathlib import Path

import pytest
from sqlalchemy import create_engine
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
