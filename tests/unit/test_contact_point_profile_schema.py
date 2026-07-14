from pathlib import Path
import sqlite3

import pytest
from sqlalchemy import inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect

from backend.infrastructure.storage.database import create_database_engine, init_db
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.models_contact_point_profile import (
    ContactPointProfileRevisionModel, ContactPointProfileRootModel,
)
from backend.shared.config import Settings


def test_point_profile_schema_registers_three_additive_tables(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    try:
        init_db(engine)
        inspector = inspect(engine)
        assert {
            "contact_point_profile_roots",
            "contact_point_profile_revisions",
            "contact_point_profile_categories",
        } <= set(inspector.get_table_names())
        indexes = {item["name"] for item in inspector.get_indexes("contact_point_profile_revisions")}
        assert {
            "uq_contact_point_profile_confirmed_per_root",
            "uq_contact_point_profile_editable_per_root",
        } <= indexes
    finally:
        engine.dispose()


def test_existing_malformed_point_profile_table_fails_closed_before_create_all(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    try:
        init_db(engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP TABLE contact_point_profile_categories")
            connection.exec_driver_sql(
                "CREATE TABLE contact_point_profile_categories ("
                "contact_point_profile_category_snapshot_id VARCHAR(64) PRIMARY KEY, "
                "contact_point_profile_revision_id VARCHAR(64) NOT NULL, category_id VARCHAR(64) NOT NULL, "
                "category_ordinal INTEGER NOT NULL, label TEXT NOT NULL, normalized_label_key TEXT NOT NULL, "
                "count_per_sample INTEGER NOT NULL, record_prefix VARCHAR(64) NOT NULL, "
                "normalized_prefix_key VARCHAR(64) NOT NULL, included BOOLEAN NOT NULL)"
            )
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(engine)
        with engine.connect() as connection:
            assert connection.exec_driver_sql("SELECT count(*) FROM contact_point_profile_roots").scalar_one() == 0
            assert {row[1] for row in connection.exec_driver_sql("PRAGMA index_list(contact_point_profile_categories)").all()} == {
                "sqlite_autoindex_contact_point_profile_categories_1"
            }
    finally:
        engine.dispose()


def test_root_only_partial_profile_schema_bootstraps_and_is_idempotent(tmp_path: Path) -> None:
    engine = _partial_engine(tmp_path, include_revision=False)
    try:
        init_db(engine)
        _assert_profile_tables(engine)
        init_db(engine)
        _assert_profile_tables(engine)
    finally:
        engine.dispose()


def test_root_and_revision_partial_profile_schema_bootstraps_and_is_idempotent(tmp_path: Path) -> None:
    engine = _partial_engine(tmp_path, include_revision=True)
    try:
        init_db(engine)
        _assert_profile_tables(engine)
        init_db(engine)
        _assert_profile_tables(engine)
    finally:
        engine.dispose()


def test_exact_v1_category_table_upgrades_in_place_and_preserves_legacy_row(tmp_path: Path) -> None:
    engine = _exact_v1_engine(tmp_path)
    try:
        v1_columns, v1_rows = _category_snapshot(engine)
        assert "point_expression" not in v1_columns
        init_db(engine)
        with engine.connect() as connection:
            ddl = connection.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='contact_point_profile_categories'"
            ).scalar_one()
        v2_columns, v2_rows = _category_snapshot(engine)
        assert v2_columns == (*v1_columns, "point_expression")
        assert len(v2_rows) == len(v1_rows)
        assert [row[:-1] for row in v2_rows] == v1_rows
        assert [row[-1] for row in v2_rows] == [None] * len(v1_rows)
        assert "ck_contact_point_profile_point_expression_nonblank" in ddl
        init_db(engine)
        assert _category_snapshot(engine) == (v2_columns, v2_rows)
    finally:
        engine.dispose()


def test_malformed_exact_v1_category_shape_fails_before_additive_upgrade(tmp_path: Path) -> None:
    engine = _exact_v1_engine(
        tmp_path,
        number_check="category_ordinal > 0 AND count_per_sample >= 0",
        category_ordinal=1,
    )
    try:
        before = _table_names(engine)
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(engine)
        assert _table_names(engine) == before
        with engine.connect() as connection:
            columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(contact_point_profile_categories)").all()}
        assert "point_expression" not in columns
    finally:
        engine.dispose()


def test_transaction_visible_final_verify_failure_rolls_back_new_profile_tables(tmp_path: Path, monkeypatch) -> None:
    from backend.infrastructure.storage import contact_point_profile_schema_migration as migration
    engine = _non_profile_engine(tmp_path)
    monkeypatch.setattr(migration, "_validate_table", lambda *_args: (_ for _ in ()).throw(RuntimeError("verify failed")))
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            migration.bootstrap_contact_point_profile_schema(engine)
        assert not ({"contact_point_profile_roots", "contact_point_profile_revisions", "contact_point_profile_categories"} & _table_names(engine))
    finally:
        engine.dispose()


def test_injected_create_failure_rolls_back_new_profile_tables(tmp_path: Path, monkeypatch) -> None:
    from backend.infrastructure.storage import contact_point_profile_schema_migration as migration
    engine = _non_profile_engine(tmp_path)
    monkeypatch.setattr(ContactPointProfileRevisionModel.__table__, "create", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("create failed")))
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            migration.bootstrap_contact_point_profile_schema(engine)
        assert not ({"contact_point_profile_roots", "contact_point_profile_revisions", "contact_point_profile_categories"} & _table_names(engine))
    finally:
        engine.dispose()


@pytest.mark.parametrize("replacement", [
    "ck_profile_wrong_name",
    "",
])
def test_named_revision_check_mismatch_fails_before_missing_category_ddl(tmp_path: Path, replacement: str) -> None:
    engine = _non_profile_engine(tmp_path)
    try:
        ContactPointProfileRootModel.__table__.create(engine)
        ddl = str(CreateTable(ContactPointProfileRevisionModel.__table__).compile(dialect=sqlite_dialect()))
        ddl = ddl.replace("ck_contact_point_profile_revision_positive", replacement) if replacement else ddl.replace(
            "CONSTRAINT ck_contact_point_profile_revision_positive ", ""
        )
        with engine.begin() as connection:
            connection.exec_driver_sql(ddl)
        before = _table_names(engine)
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            init_db(engine)
        assert _table_names(engine) == before
        assert "contact_point_profile_categories" not in before
    finally:
        engine.dispose()


def test_locked_writer_fails_closed_then_bootstraps_after_release(tmp_path: Path) -> None:
    from backend.infrastructure.storage import contact_point_profile_schema_migration as migration
    engine = _non_profile_engine(tmp_path, connect_args={"timeout": 0})
    locker = sqlite3.connect(_settings(tmp_path).database_path)
    try:
        locker.execute("BEGIN IMMEDIATE")
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            migration.bootstrap_contact_point_profile_schema(engine)
        assert not ({"contact_point_profile_roots", "contact_point_profile_revisions", "contact_point_profile_categories"} & _table_names(engine))
        locker.rollback()
        migration.bootstrap_contact_point_profile_schema(engine)
        _assert_profile_tables(engine)
    finally:
        locker.close()
        engine.dispose()


def _partial_engine(tmp_path: Path, *, include_revision: bool):
    from backend.infrastructure.storage import models, models_confirmed_matrix_authority, models_contact_measurement_plan_authority
    from backend.infrastructure.storage import models_matrix_source, models_project_matrix_draft
    engine = _non_profile_engine(tmp_path)
    ContactPointProfileRootModel.__table__.create(engine)
    if include_revision:
        ContactPointProfileRevisionModel.__table__.create(engine)
    return engine


def _exact_v1_engine(
    tmp_path: Path,
    *,
    number_check: str = "category_ordinal >= 0 AND count_per_sample >= 0",
    category_ordinal: int = 0,
):
    engine = _partial_engine(tmp_path, include_revision=True)
    v1_category_ddl = (
        "CREATE TABLE contact_point_profile_categories ("
        "contact_point_profile_category_snapshot_id VARCHAR(64) NOT NULL, "
        "contact_point_profile_revision_id VARCHAR(64) NOT NULL, category_id VARCHAR(64) NOT NULL, "
        "category_ordinal INTEGER NOT NULL, label TEXT NOT NULL, normalized_label_key TEXT NOT NULL, "
        "count_per_sample INTEGER NOT NULL, record_prefix VARCHAR(64) NOT NULL, "
        "normalized_prefix_key VARCHAR(64) NOT NULL, included BOOLEAN NOT NULL, "
        "PRIMARY KEY (contact_point_profile_category_snapshot_id), "
        "CONSTRAINT uq_contact_point_profile_category_order UNIQUE (contact_point_profile_revision_id, category_ordinal), "
        "CONSTRAINT uq_contact_point_profile_category_id UNIQUE (contact_point_profile_revision_id, category_id), "
        f"CONSTRAINT ck_contact_point_profile_category_numbers CHECK ({number_check}), "
        "CONSTRAINT ck_contact_point_profile_included_count CHECK (included = 0 OR count_per_sample > 0), "
        "FOREIGN KEY(contact_point_profile_revision_id) REFERENCES contact_point_profile_revisions (contact_point_profile_revision_id))"
    )
    with engine.begin() as connection:
        connection.exec_driver_sql(v1_category_ddl)
        connection.exec_driver_sql(
            "CREATE UNIQUE INDEX uq_contact_point_profile_included_label ON contact_point_profile_categories "
            "(contact_point_profile_revision_id, normalized_label_key) WHERE included = 1"
        )
        connection.exec_driver_sql(
            "CREATE UNIQUE INDEX uq_contact_point_profile_included_prefix ON contact_point_profile_categories "
            "(contact_point_profile_revision_id, normalized_prefix_key) WHERE included = 1"
        )
        connection.exec_driver_sql(
            "INSERT INTO contact_point_profile_roots "
            "(contact_point_profile_root_id, project_id, active_confirmed_revision_id, editable_revision_id, created_at, updated_at) "
            "VALUES ('root-1', 'project-1', 'revision-1', NULL, '2026-07-15T00:00:00Z', '2026-07-15T00:00:00Z')"
        )
        connection.exec_driver_sql(
            "INSERT INTO contact_point_profile_revisions "
            "(contact_point_profile_revision_id, contact_point_profile_root_id, revision_sequence, parent_revision_id, state, "
            "revision_fingerprint, bootstrap_provenance, created_by, created_at, updated_at, confirmed_by, confirmed_at, superseded_at, superseded_reason) "
            "VALUES ('revision-1', 'root-1', 1, NULL, 'confirmed', 'legacy-fingerprint', NULL, 'operator', "
            "'2026-07-15T00:00:00Z', '2026-07-15T00:00:00Z', 'operator', '2026-07-15T00:00:00Z', NULL, NULL)"
        )
        connection.exec_driver_sql(
            "INSERT INTO contact_point_profile_categories "
            "(contact_point_profile_category_snapshot_id, contact_point_profile_revision_id, category_id, category_ordinal, "
            "label, normalized_label_key, count_per_sample, record_prefix, normalized_prefix_key, included) "
            f"VALUES ('category-1', 'revision-1', 'ppc-1', {category_ordinal}, 'High Power', 'high power', 4, 'HP', 'hp', 1)"
        )
    return engine


def _category_snapshot(engine) -> tuple[tuple[str, ...], list[tuple[object, ...]]]:
    with engine.connect() as connection:
        columns = tuple(str(row[1]) for row in connection.exec_driver_sql("PRAGMA table_info(contact_point_profile_categories)").all())
        quoted = ", ".join(f'"{column}"' for column in columns)
        rows = connection.exec_driver_sql(
            f"SELECT {quoted} FROM contact_point_profile_categories "
            "ORDER BY category_ordinal, contact_point_profile_category_snapshot_id"
        ).all()
    return columns, rows


def _non_profile_engine(tmp_path: Path, **engine_options):
    from backend.infrastructure.storage import models, models_confirmed_matrix_authority, models_contact_measurement_plan_authority
    from backend.infrastructure.storage import models_matrix_source, models_project_matrix_draft
    engine = create_database_engine(_settings(tmp_path), **engine_options)
    profile = {"contact_point_profile_roots", "contact_point_profile_revisions", "contact_point_profile_categories"}
    Base.metadata.create_all(engine, tables=[table for table in Base.metadata.tables.values() if table.name not in profile])
    return engine


def _assert_profile_tables(engine) -> None:
    assert {"contact_point_profile_roots", "contact_point_profile_revisions", "contact_point_profile_categories"} <= _table_names(engine)


def _table_names(engine) -> set[str]:
    with engine.connect() as connection:
        return {row[0] for row in connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").all()}


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "data" / "connlab.sqlite3",
    )
