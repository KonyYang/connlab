"""SQLite migration for Matrix draft lifecycle reconciliation."""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Engine


def reconcile_project_matrix_draft_lifecycle(engine: Engine) -> None:
    """Archive confirmed lineage and retain at most one unreferenced working draft."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if not {
            "project_matrix_draft_records",
            "confirmed_matrix_versions",
        } <= table_names:
            return
        if not _supports_lifecycle_reconciliation(connection):
            return

        connection.exec_driver_sql(
            """
            UPDATE project_matrix_draft_records
            SET status = 'superseded'
            WHERE project_matrix_draft_id IN (
                SELECT project_matrix_draft_id
                FROM confirmed_matrix_versions
            )
            """
        )
        project_ids = connection.exec_driver_sql(
            "SELECT DISTINCT project_id FROM project_matrix_draft_records"
        ).all()
        for (project_id,) in project_ids:
            current_id = _current_working_draft_id(connection, str(project_id))
            stale_rows = connection.exec_driver_sql(
                """
                SELECT project_matrix_draft_id
                FROM project_matrix_draft_records
                WHERE project_id = ?
                  AND status = 'draft'
                  AND NOT EXISTS (
                      SELECT 1 FROM confirmed_matrix_versions
                      WHERE confirmed_matrix_versions.project_matrix_draft_id =
                            project_matrix_draft_records.project_matrix_draft_id
                  )
                  AND (? IS NULL OR project_matrix_draft_id <> ?)
                """,
                (project_id, current_id, current_id),
            ).all()
            for (draft_id,) in stale_rows:
                _delete_unreferenced_draft(
                    connection,
                    table_names=table_names,
                    draft_id=str(draft_id),
                )
        connection.exec_driver_sql(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_project_matrix_draft_one_working
            ON project_matrix_draft_records(project_id)
            WHERE status = 'draft'
            """
        )


def _supports_lifecycle_reconciliation(connection: Any) -> bool:
    draft_columns = _column_names(connection, "project_matrix_draft_records")
    confirmed_columns = _column_names(connection, "confirmed_matrix_versions")
    return {
        "project_matrix_draft_id",
        "project_id",
        "source_import_id",
        "base_confirmed_matrix_id",
        "status",
        "updated_at",
    } <= draft_columns and {
        "project_matrix_draft_id",
        "project_id",
        "confirmed_matrix_id",
        "source_import_id",
        "confirmed_revision",
        "is_active_authority",
        "confirmed_at",
    } <= confirmed_columns


def _column_names(connection: Any, table_name: str) -> set[str]:
    return {
        str(row[1])
        for row in connection.exec_driver_sql(f"PRAGMA table_info({table_name})").all()
    }


def _current_working_draft_id(connection: Any, project_id: str) -> str | None:
    active = connection.exec_driver_sql(
        """
        SELECT confirmed_matrix_id, source_import_id, confirmed_at
        FROM confirmed_matrix_versions
        WHERE project_id = ? AND is_active_authority = 1
        ORDER BY confirmed_revision DESC
        LIMIT 1
        """,
        (project_id,),
    ).first()
    if active is None:
        row = connection.exec_driver_sql(
            """
            SELECT project_matrix_draft_id
            FROM project_matrix_draft_records
            WHERE project_id = ?
              AND status = 'draft'
              AND base_confirmed_matrix_id IS NULL
              AND NOT EXISTS (
                  SELECT 1 FROM confirmed_matrix_versions
                  WHERE confirmed_matrix_versions.project_matrix_draft_id =
                        project_matrix_draft_records.project_matrix_draft_id
              )
            ORDER BY updated_at DESC, project_matrix_draft_id DESC
            LIMIT 1
            """,
            (project_id,),
        ).first()
    else:
        row = connection.exec_driver_sql(
            """
            SELECT project_matrix_draft_id
            FROM project_matrix_draft_records
            WHERE project_id = ?
              AND status = 'draft'
              AND NOT EXISTS (
                  SELECT 1 FROM confirmed_matrix_versions
                  WHERE confirmed_matrix_versions.project_matrix_draft_id =
                        project_matrix_draft_records.project_matrix_draft_id
              )
              AND (
                  base_confirmed_matrix_id = ?
                  OR (
                      base_confirmed_matrix_id IS NULL
                      AND (source_import_id IS NULL OR source_import_id <> ?)
                      AND updated_at > ?
                  )
              )
            ORDER BY updated_at DESC, project_matrix_draft_id DESC
            LIMIT 1
            """,
            (project_id, active[0], active[1], active[2]),
        ).first()
    return str(row[0]) if row is not None else None


def _delete_unreferenced_draft(
    connection: Any,
    *,
    table_names: set[str],
    draft_id: str,
) -> None:
    for table_name in (
        "matrix_fee_pending_rebases",
        "project_matrix_draft_duration_authorities",
        "project_matrix_draft_step_quantities",
        "project_matrix_draft_cells",
        "project_matrix_draft_groups",
        "project_matrix_draft_rows",
    ):
        if table_name in table_names:
            connection.exec_driver_sql(
                f"DELETE FROM {table_name} WHERE project_matrix_draft_id = ?",
                (draft_id,),
            )
    connection.exec_driver_sql(
        "DELETE FROM project_matrix_draft_records WHERE project_matrix_draft_id = ?",
        (draft_id,),
    )
