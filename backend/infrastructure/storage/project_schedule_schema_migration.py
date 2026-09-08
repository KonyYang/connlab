"""Fail-closed additive bootstrap for independent Project Schedule authority."""

from __future__ import annotations


_COLUMNS = {
    "revision_id": ("VARCHAR(64)", 1, 1),
    "project_id": ("VARCHAR(64)", 1, 0),
    "revision_sequence": ("INTEGER", 1, 0),
    "state": ("VARCHAR(32)", 1, 0),
    "fingerprint": ("VARCHAR(128)", 1, 0),
    "matrix_input_fingerprint": ("VARCHAR(128)", 1, 0),
    "based_on_confirmed_matrix_id": ("VARCHAR(64)", 1, 0),
    "based_on_confirmed_matrix_revision": ("INTEGER", 1, 0),
    "based_on_basic_information_version": ("INTEGER", 1, 0),
    "sample_received_date": ("VARCHAR(32)", 1, 0),
    "post_test_buffer_days": ("VARCHAR(64)", 1, 0),
    "test_start_date": ("VARCHAR(32)", 1, 0),
    "test_complete_date": ("VARCHAR(32)", 1, 0),
    "estimated_completion_date": ("VARCHAR(32)", 1, 0),
    "confirmed_by": ("VARCHAR(255)", 1, 0),
    "confirmed_at": ("VARCHAR(64)", 1, 0),
    "superseded_at": ("VARCHAR(64)", 0, 0),
    "superseded_reason": ("TEXT", 0, 0),
}


def bootstrap_project_schedule_schema(engine) -> None:
    """Create a missing schedule table, but never repair an incompatible one."""
    if engine.dialect.name != "sqlite":
        return
    # Register FK targets before compiling the dedicated table DDL.
    from backend.infrastructure.storage import models  # noqa: F401
    from backend.infrastructure.storage import models_confirmed_matrix_authority  # noqa: F401
    from backend.infrastructure.storage.models_project_schedule import (
        ProjectScheduleRevisionModel,
    )

    table = ProjectScheduleRevisionModel.__table__
    with engine.connect() as connection:
        exists = connection.exec_driver_sql(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table.name,),
        ).scalar_one_or_none()
        if exists:
            _validate(connection)
            return
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            table.create(connection, checkfirst=False)
            _validate(connection)
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("authority_corrupt: Project Schedule bootstrap failed.") from exc


def _validate(connection) -> None:
    columns = {
        str(row[1]): (str(row[2]).upper(), int(row[3]), int(row[5]))
        for row in connection.exec_driver_sql(
            "PRAGMA table_info(project_schedule_revisions)"
        ).all()
    }
    if columns != _COLUMNS:
        _corrupt()
    fks = {
        (str(row[3]), str(row[2]), str(row[4]))
        for row in connection.exec_driver_sql(
            "PRAGMA foreign_key_list(project_schedule_revisions)"
        ).all()
    }
    if fks != {
        ("project_id", "projects", "project_id"),
        (
            "based_on_confirmed_matrix_id",
            "confirmed_matrix_versions",
            "confirmed_matrix_id",
        ),
    }:
        _corrupt()
    sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='project_schedule_revisions'"
    ).scalar_one_or_none() or ""
    compact = "".join(sql.lower().split())
    if "revision_sequence>0" not in compact or "statein('confirmed','superseded')" not in compact:
        _corrupt()
    indexes = {
        str(row[1]): (bool(row[2]), bool(row[4]))
        for row in connection.exec_driver_sql(
            "PRAGMA index_list(project_schedule_revisions)"
        ).all()
    }
    active = indexes.get("uq_project_schedule_active_per_project")
    if active != (True, True):
        _corrupt()


def _corrupt() -> None:
    raise RuntimeError("authority_corrupt: Project Schedule schema is incompatible.")
