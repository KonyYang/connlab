import pytest
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError

from backend.infrastructure.storage.project_schedule_schema_migration import (
    bootstrap_project_schedule_schema,
)


def test_bootstrap_creates_project_schedule_authority_table() -> None:
    engine = create_engine("sqlite://", future=True)

    bootstrap_project_schedule_schema(engine)

    assert "project_schedule_revisions" in inspect(engine).get_table_names()


def test_bootstrap_rejects_incompatible_existing_project_schedule_table() -> None:
    engine = create_engine("sqlite://", future=True)
    with engine.begin() as connection:
        connection.execute(text("create table project_schedule_revisions (revision_id text primary key)"))

    with pytest.raises(RuntimeError, match="authority_corrupt: Project Schedule"):
        bootstrap_project_schedule_schema(engine)


def test_legacy_migration_preserves_history_indexes_constraints_and_allows_missing_lineage():
    engine = _legacy_engine()
    before = _snapshot(engine)
    bootstrap_project_schedule_schema(engine)
    bootstrap_project_schedule_schema(engine)
    after = _snapshot(engine)
    assert after[1:] == before[1:]
    assert {column["name"] for column in inspect(engine).get_columns("project_schedule_revisions") if column["nullable"]} == {
        "based_on_confirmed_matrix_id", "based_on_confirmed_matrix_revision", "based_on_basic_information_version",
        "superseded_at", "superseded_reason",
    }
    with engine.begin() as connection:
        connection.exec_driver_sql("UPDATE project_schedule_revisions SET state='superseded' WHERE revision_id='S2'")
        _insert(connection, "S3", 3, "confirmed", lineage=None)
    for revision_id, sequence, state, project_id, lineage in [
        ("S4", 4, "confirmed", "P1", None), ("S4", 0, "superseded", "P1", None),
        ("S4", 4, "draft", "P1", None), ("S4", 2, "superseded", "P1", None),
        ("S4", 4, "superseded", "missing", None), ("S4", 4, "superseded", "P1", "missing"),
    ]:
        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert(connection, revision_id, sequence, state, project_id=project_id, lineage=lineage)


@pytest.mark.parametrize("failure_statement", ["DROP TABLE", "ALTER TABLE", "CREATE INDEX"])
def test_migration_rolls_back_the_complete_database_on_mid_rebuild_failure(failure_statement):
    engine = _legacy_engine()
    before = _snapshot(engine)

    def fail_drop(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith(failure_statement):
            raise RuntimeError("injected DDL failure")

    event.listen(engine, "before_cursor_execute", fail_drop)
    try:
        with pytest.raises(RuntimeError, match="authority_corrupt"):
            bootstrap_project_schedule_schema(engine)
    finally:
        event.remove(engine, "before_cursor_execute", fail_drop)
    assert _snapshot(engine) == before
    assert inspect(engine).get_table_names() == ["confirmed_matrix_versions", "project_schedule_revisions", "projects"]


@pytest.mark.parametrize("variant", ["extra_column", "missing_unique", "wrong_partial", "trigger", "incoming_fk", "default", "extra_check"])
def test_migration_rejects_unknown_schema_without_changing_records(variant):
    engine = _legacy_engine(variant)
    before = _snapshot(engine)
    with pytest.raises(RuntimeError, match="authority_corrupt"):
        bootstrap_project_schedule_schema(engine)
    assert _snapshot(engine) == before


_LEGACY_DDL = """CREATE TABLE project_schedule_revisions (
    revision_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64) NOT NULL,
    revision_sequence INTEGER NOT NULL,
    state VARCHAR(32) NOT NULL,
    fingerprint VARCHAR(128) NOT NULL,
    matrix_input_fingerprint VARCHAR(128) NOT NULL,
    based_on_confirmed_matrix_id VARCHAR(64) NOT NULL,
    based_on_confirmed_matrix_revision INTEGER NOT NULL,
    based_on_basic_information_version INTEGER NOT NULL,
    sample_received_date VARCHAR(32) NOT NULL,
    post_test_buffer_days VARCHAR(64) NOT NULL,
    test_start_date VARCHAR(32) NOT NULL,
    test_complete_date VARCHAR(32) NOT NULL,
    estimated_completion_date VARCHAR(32) NOT NULL,
    confirmed_by VARCHAR(255) NOT NULL,
    confirmed_at VARCHAR(64) NOT NULL,
    superseded_at VARCHAR(64),
    superseded_reason TEXT,
    PRIMARY KEY (revision_id),
    CONSTRAINT uq_project_schedule_revision_sequence UNIQUE (project_id, revision_sequence),
    CONSTRAINT ck_project_schedule_revision_positive CHECK (revision_sequence > 0),
    CONSTRAINT ck_project_schedule_revision_state CHECK (state IN ('confirmed','superseded')),
    FOREIGN KEY(project_id) REFERENCES projects (project_id),
    FOREIGN KEY(based_on_confirmed_matrix_id) REFERENCES confirmed_matrix_versions (confirmed_matrix_id)
)"""


def _legacy_engine(variant=None):
    engine = create_engine("sqlite://", future=True)
    ddl = _LEGACY_DDL
    if variant == "missing_unique":
        ddl = ddl.replace("CONSTRAINT uq_project_schedule_revision_sequence UNIQUE (project_id, revision_sequence),", "")
    if variant == "default":
        ddl = ddl.replace("confirmed_by VARCHAR(255) NOT NULL", "confirmed_by VARCHAR(255) NOT NULL DEFAULT 'User'")
    if variant == "extra_check":
        ddl = ddl.replace("superseded_reason TEXT,", "superseded_reason TEXT CHECK (length(superseded_reason) < 100),")
    with engine.begin() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
        connection.exec_driver_sql("CREATE TABLE projects (project_id VARCHAR(64) PRIMARY KEY)")
        connection.exec_driver_sql("CREATE TABLE confirmed_matrix_versions (confirmed_matrix_id VARCHAR(64) PRIMARY KEY)")
        connection.exec_driver_sql("INSERT INTO projects VALUES ('P1')")
        connection.exec_driver_sql("INSERT INTO confirmed_matrix_versions VALUES ('M1')")
        connection.exec_driver_sql(ddl)
        connection.exec_driver_sql("CREATE UNIQUE INDEX uq_project_schedule_active_per_project ON project_schedule_revisions(project_id) WHERE state='confirmed'")
        connection.exec_driver_sql("CREATE INDEX ix_project_schedule_revisions_project_id ON project_schedule_revisions(project_id)")
        connection.exec_driver_sql("CREATE INDEX ix_project_schedule_revisions_state ON project_schedule_revisions(state)")
        connection.exec_driver_sql("CREATE INDEX custom_schedule_actor ON project_schedule_revisions(confirmed_by, confirmed_at)")
        _insert(connection, "S1", 1, "superseded")
        _insert(connection, "S2", 2, "confirmed")
        if variant == "extra_column":
            connection.exec_driver_sql("ALTER TABLE project_schedule_revisions ADD COLUMN custom TEXT")
        if variant == "wrong_partial":
            connection.exec_driver_sql("DROP INDEX uq_project_schedule_active_per_project")
            connection.exec_driver_sql("CREATE UNIQUE INDEX uq_project_schedule_active_per_project ON project_schedule_revisions(project_id) WHERE state='superseded'")
        if variant == "trigger":
            connection.exec_driver_sql("CREATE TRIGGER schedule_trigger AFTER DELETE ON project_schedule_revisions BEGIN DELETE FROM projects; END")
        if variant == "incoming_fk":
            connection.exec_driver_sql("CREATE TABLE consumer (schedule_id VARCHAR(64) REFERENCES project_schedule_revisions(revision_id) ON DELETE CASCADE)")
            connection.exec_driver_sql("INSERT INTO consumer VALUES ('S2')")
    return engine


def _insert(connection, revision_id, sequence, state, *, project_id="P1", lineage="M1"):
    connection.exec_driver_sql("""INSERT INTO project_schedule_revisions
        (revision_id, project_id, revision_sequence, state, fingerprint, matrix_input_fingerprint,
         based_on_confirmed_matrix_id, based_on_confirmed_matrix_revision, based_on_basic_information_version,
         sample_received_date, post_test_buffer_days, test_start_date, test_complete_date,
         estimated_completion_date, confirmed_by, confirmed_at, superseded_at, superseded_reason)
        VALUES (?, ?, ?, ?, 'fp', 'matrix-fp', ?, ?, ?, '', '2', '2026-09-02', '2026-09-05',
                '2026-09-07', '测试员', '2026-09-01T00:00:00Z', ?, ?)""",
        (revision_id, project_id, sequence, state, lineage, 1 if lineage else None, 2 if lineage else None,
         "2026-09-08T00:00:00Z" if state == "superseded" else None,
         "历史记录" if state == "superseded" else None))


def _snapshot(engine):
    with engine.connect() as connection:
        schema = connection.exec_driver_sql("SELECT name, type, sql FROM sqlite_master ORDER BY name").all()
        records = connection.exec_driver_sql("SELECT * FROM project_schedule_revisions ORDER BY revision_id").all()
        indexes = connection.exec_driver_sql("SELECT name, sql FROM sqlite_master WHERE type='index' ORDER BY name").all()
        projects = connection.exec_driver_sql("SELECT * FROM projects").all()
        matrices = connection.exec_driver_sql("SELECT * FROM confirmed_matrix_versions").all()
        return schema, records, indexes, projects, matrices
