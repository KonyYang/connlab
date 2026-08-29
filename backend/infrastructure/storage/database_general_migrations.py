"""General SQLite compatibility migrations."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.engine import Engine


def _migrate_project_no_optional(engine: Engine) -> None:
    """Relax legacy project_no NOT NULL/UNIQUE constraints in local SQLite DBs."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "projects" not in table_names:
            return
        columns = connection.exec_driver_sql("PRAGMA table_info(projects)").all()
        project_no_column = next((row for row in columns if row[1] == "project_no"), None)
        if project_no_column is None or not bool(project_no_column[3]):
            if not _has_single_column_unique_index(connection, "projects", "project_no"):
                return

        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        try:
            connection.exec_driver_sql(
                """
                CREATE TABLE projects_new (
                    project_id VARCHAR(64) NOT NULL,
                    project_no VARCHAR(128),
                    product_name VARCHAR(255) NOT NULL,
                    requestor VARCHAR(255) NOT NULL,
                    status VARCHAR(64) NOT NULL,
                    business_unit VARCHAR(255),
                    created_on DATE,
                    PRIMARY KEY (project_id)
                )
                """
            )
            connection.exec_driver_sql(
                """
                INSERT INTO projects_new (
                    project_id,
                    project_no,
                    product_name,
                    requestor,
                    status,
                    business_unit,
                    created_on
                )
                SELECT
                    project_id,
                    NULLIF(project_no, ''),
                    product_name,
                    requestor,
                    status,
                    business_unit,
                    created_on
                FROM projects
                """
            )
            connection.exec_driver_sql("DROP TABLE projects")
            connection.exec_driver_sql("ALTER TABLE projects_new RENAME TO projects")
        finally:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")

def _has_single_column_unique_index(connection: Any, table: str, column: str) -> bool:
    """Return whether a table has a unique index only on one named column."""
    for index in connection.exec_driver_sql(f"PRAGMA index_list({table})").all():
        if not bool(index[2]):
            continue
        indexed_columns = [
            row[2]
            for row in connection.exec_driver_sql(f"PRAGMA index_info({index[1]})").all()
        ]
        if indexed_columns == [column]:
            return True
    return False

def _migrate_file_asset_provenance_columns(engine: Engine) -> None:
    """Add optional TASK_317 file-asset provenance columns to existing SQLite DBs."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "file_assets" not in table_names:
            return
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(file_assets)").all()
        }
        for column in (
            "source_package_id",
            "source_intake_asset_id",
            "source_role",
            "sha256",
        ):
            if column in columns:
                continue
            connection.exec_driver_sql(
                f"ALTER TABLE file_assets ADD COLUMN {column} VARCHAR(64)"
            )

def _migrate_project_output_record_file_metadata(engine: Engine) -> None:
    """Add optional TASK_321 managed-output metadata columns to output records."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "project_output_records" not in table_names:
            return
        columns = {
            row[1]
            for row in connection.exec_driver_sql(
                "PRAGMA table_info(project_output_records)"
            ).all()
        }
        column_defs = {
            "output_sha256": "VARCHAR(128)",
            "output_size_bytes": "INTEGER",
            "source_context_signature": "VARCHAR(512)",
        }
        for column, definition in column_defs.items():
            if column in columns:
                continue
            connection.exec_driver_sql(
                f"ALTER TABLE project_output_records ADD COLUMN {column} {definition}"
            )

def _migrate_project_basic_information_records_table(engine: Engine) -> None:
    """Create TASK_330A Basic Information records table for local SQLite DBs."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "project_basic_information_records" in table_names:
            return
        connection.exec_driver_sql(
            """
            CREATE TABLE project_basic_information_records (
                record_id VARCHAR(64) NOT NULL,
                project_id VARCHAR(64) NOT NULL,
                status VARCHAR(32) NOT NULL,
                version INTEGER NOT NULL,
                values_json TEXT NOT NULL,
                source_signature_json TEXT NOT NULL,
                created_at VARCHAR(64) NOT NULL,
                updated_at VARCHAR(64) NOT NULL,
                confirmed_at VARCHAR(64),
                confirmed_by VARCHAR(255),
                PRIMARY KEY (record_id),
                CONSTRAINT uq_project_basic_information_project_status_version
                    UNIQUE (project_id, status, version),
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
            """
        )
        connection.exec_driver_sql(
            "CREATE INDEX ix_project_basic_information_records_project_id "
            "ON project_basic_information_records(project_id)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX ix_project_basic_information_records_status "
            "ON project_basic_information_records(status)"
        )


def _migrate_report_sample_authority_columns(engine: Engine) -> None:
    """Add REPORT-001D sample lineage and confirmed-snapshot columns."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "sample_infos" in table_names:
            columns = {
                row[1]
                for row in connection.exec_driver_sql(
                    "PRAGMA table_info(sample_infos)"
                ).all()
            }
            column_defs = {
                "lubricant": "VARCHAR(255)",
                "row_index": "INTEGER NOT NULL DEFAULT 0",
                "source_form_id": "VARCHAR(64)",
            }
            added_row_index = "row_index" not in columns
            for column, definition in column_defs.items():
                if column in columns:
                    continue
                connection.exec_driver_sql(
                    f"ALTER TABLE sample_infos ADD COLUMN {column} {definition}"
                )
            if added_row_index:
                connection.exec_driver_sql(
                    """
                    UPDATE sample_infos AS current
                    SET row_index = (
                        SELECT COUNT(*) - 1
                        FROM sample_infos AS preceding
                        WHERE preceding.project_id = current.project_id
                          AND preceding.rowid <= current.rowid
                    )
                    """
                )
            if "application_forms" in table_names:
                connection.exec_driver_sql(
                    """
                    UPDATE sample_infos
                    SET source_form_id = (
                        SELECT form_id
                        FROM application_forms
                        WHERE application_forms.project_id = sample_infos.project_id
                        ORDER BY application_forms.rowid DESC
                        LIMIT 1
                    )
                    WHERE source_form_id IS NULL
                    """
                )
            if {"intake_cases", "intake_drafts"} <= table_names:
                legacy_drafts = connection.exec_driver_sql(
                    """
                    SELECT
                        intake_cases.confirmed_project_id,
                        intake_drafts.parsed_fields_json,
                        intake_drafts.manual_overrides_json
                    FROM intake_cases
                    JOIN intake_drafts
                      ON intake_drafts.case_id = intake_cases.case_id
                    WHERE intake_cases.confirmed_project_id IS NOT NULL
                    ORDER BY intake_cases.rowid
                    """
                ).all()
                for project_id, parsed_json, overrides_json in legacy_drafts:
                    try:
                        parsed = json.loads(parsed_json or "{}")
                        overrides = json.loads(overrides_json or "{}")
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(parsed, dict) or not isinstance(overrides, dict):
                        continue
                    merged = {
                        **parsed,
                        **{
                            key: value
                            for key, value in overrides.items()
                            if value not in (None, "")
                        },
                    }
                    source_rows = merged.get("samples")
                    if not isinstance(source_rows, list):
                        continue
                    persisted_rows = connection.exec_driver_sql(
                        """
                        SELECT sample_id, lubricant
                        FROM sample_infos
                        WHERE project_id = ?
                        ORDER BY row_index, rowid
                        """,
                        (project_id,),
                    ).all()
                    for persisted, source in zip(
                        persisted_rows,
                        source_rows,
                        strict=False,
                    ):
                        if persisted[1] not in (None, "") or not isinstance(source, dict):
                            continue
                        lubricant = str(source.get("lubricant") or "").strip()
                        if not lubricant:
                            continue
                        connection.exec_driver_sql(
                            "UPDATE sample_infos SET lubricant = ? WHERE sample_id = ?",
                            (lubricant, persisted[0]),
                        )

        if "project_basic_information_records" in table_names:
            columns = {
                row[1]
                for row in connection.exec_driver_sql(
                    "PRAGMA table_info(project_basic_information_records)"
                ).all()
            }
            if "sample_rows_json" not in columns:
                connection.exec_driver_sql(
                    "ALTER TABLE project_basic_information_records "
                    "ADD COLUMN sample_rows_json TEXT"
                )
            if "sample_infos" in table_names:
                rows_by_project: dict[str, list[dict[str, object]]] = {}
                sample_rows = connection.exec_driver_sql(
                    """
                    SELECT
                        project_id,
                        product_name,
                        part_number,
                        lot_or_traceability,
                        material,
                        plating,
                        lubricant,
                        housing_material,
                        revision,
                        quantity,
                        row_index,
                        source_form_id
                    FROM sample_infos
                    ORDER BY project_id, row_index, rowid
                    """
                ).all()
                for row in sample_rows:
                    rows_by_project.setdefault(str(row[0]), []).append(
                        {
                            "product_name": row[1] or "",
                            "part_number": row[2] or "",
                            "lot_or_traceability": row[3] or "",
                            "material": row[4] or "",
                            "plating": row[5] or "",
                            "lubricant": row[6] or "",
                            "housing_material": row[7] or "",
                            "revision": row[8] or "",
                            "quantity": row[9],
                            "row_index": row[10],
                            "source_form_id": row[11],
                        }
                    )
                for project_id, rows in rows_by_project.items():
                    connection.exec_driver_sql(
                        """
                        UPDATE project_basic_information_records
                        SET sample_rows_json = ?
                        WHERE project_id = ?
                          AND (sample_rows_json IS NULL OR sample_rows_json = '')
                        """,
                        (
                            json.dumps(rows, ensure_ascii=False, sort_keys=True),
                            project_id,
                        ),
                    )

def _migrate_project_lifecycle_columns(engine: Engine) -> None:
    """Add TASK_337A lifecycle overlay columns and backfill legacy project rows."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "projects" not in table_names:
            return

        columns = {
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(projects)").all()
        }
        column_defs = {
            "lifecycle_state": "VARCHAR(32)",
            "closure_type": "VARCHAR(32)",
            "close_reason_category": "VARCHAR(32)",
            "stopped_reason": "TEXT",
            "stopped_at": "VARCHAR(64)",
            "stopped_by": "VARCHAR(255)",
            "resumed_reason": "TEXT",
            "resumed_at": "VARCHAR(64)",
            "resumed_by": "VARCHAR(255)",
            "closed_reason": "TEXT",
            "closed_at": "VARCHAR(64)",
            "closed_by": "VARCHAR(255)",
            "completion_summary_json": "TEXT",
        }
        for column, definition in column_defs.items():
            if column in columns:
                continue
            connection.exec_driver_sql(
                f"ALTER TABLE projects ADD COLUMN {column} {definition}"
            )

        connection.exec_driver_sql(
            """
            UPDATE projects
            SET lifecycle_state = 'stopped'
            WHERE (lifecycle_state IS NULL OR lifecycle_state = '')
                AND status = 'cancelled'
            """
        )
        connection.exec_driver_sql(
            """
            UPDATE projects
            SET lifecycle_state = 'closed'
            WHERE (lifecycle_state IS NULL OR lifecycle_state = '')
                AND status = 'closed'
            """
        )
        connection.exec_driver_sql(
            """
            UPDATE projects
            SET lifecycle_state = 'active'
            WHERE lifecycle_state IS NULL OR lifecycle_state = ''
            """
        )
        connection.exec_driver_sql(
            """
            UPDATE projects
            SET closure_type = 'administrative'
            WHERE lifecycle_state = 'closed'
                AND status = 'closed'
                AND (closure_type IS NULL OR closure_type = '')
            """
        )
        connection.exec_driver_sql(
            """
            UPDATE projects
            SET close_reason_category = 'completed'
            WHERE lifecycle_state = 'closed'
                AND closure_type = 'completed'
                AND (close_reason_category IS NULL OR close_reason_category = '')
            """
        )
        connection.exec_driver_sql(
            """
            UPDATE projects
            SET close_reason_category = 'other'
            WHERE lifecycle_state = 'closed'
                AND (closure_type = 'administrative'
                    OR closure_type IS NULL
                    OR closure_type = '')
                AND (close_reason_category IS NULL OR close_reason_category = '')
            """
        )

def _migrate_ltr_duplicate_resolution_tables(engine: Engine) -> None:
    """Add local LTR duplicate-resolution owner, token, and audit storage."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "ltr_records" in table_names:
            columns = {
                row[1]
                for row in connection.exec_driver_sql("PRAGMA table_info(ltr_records)").all()
            }
            needs_rebuild = (
                "is_current_owner" not in columns
                or _has_single_column_unique_index(connection, "ltr_records", "ltr_number")
            )
            if needs_rebuild:
                connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
                try:
                    connection.exec_driver_sql(
                        """
                        CREATE TABLE ltr_records_new (
                            ltr_id VARCHAR(64) NOT NULL,
                            project_id VARCHAR(64) NOT NULL,
                            ltr_number VARCHAR(128) NOT NULL,
                            status VARCHAR(64) NOT NULL,
                            registered_on DATE,
                            requested_by VARCHAR(255),
                            requested_date DATE,
                            notes TEXT,
                            is_current_owner BOOLEAN NOT NULL DEFAULT 1,
                            superseded_at VARCHAR(64),
                            superseded_by_ltr_id VARCHAR(64),
                            superseded_reason TEXT,
                            owner_version INTEGER NOT NULL DEFAULT 1,
                            PRIMARY KEY (ltr_id),
                            FOREIGN KEY(project_id) REFERENCES projects(project_id)
                        )
                        """
                    )
                    existing_columns = columns
                    select_values = [
                        "ltr_id",
                        "project_id",
                        "ltr_number",
                        "status",
                        "registered_on",
                        "requested_by",
                        "requested_date",
                        "notes",
                        (
                            "is_current_owner"
                            if "is_current_owner" in existing_columns
                            else "CASE WHEN status = 'registered' THEN 1 ELSE 0 END"
                        ),
                        (
                            "superseded_at"
                            if "superseded_at" in existing_columns
                            else "NULL"
                        ),
                        (
                            "superseded_by_ltr_id"
                            if "superseded_by_ltr_id" in existing_columns
                            else "NULL"
                        ),
                        (
                            "superseded_reason"
                            if "superseded_reason" in existing_columns
                            else "NULL"
                        ),
                        (
                            "owner_version"
                            if "owner_version" in existing_columns
                            else "1"
                        ),
                    ]
                    connection.exec_driver_sql(
                        """
                        INSERT INTO ltr_records_new (
                            ltr_id,
                            project_id,
                            ltr_number,
                            status,
                            registered_on,
                            requested_by,
                            requested_date,
                            notes,
                            is_current_owner,
                            superseded_at,
                            superseded_by_ltr_id,
                            superseded_reason,
                            owner_version
                        )
                        SELECT
                        """
                        + ",\n".join(select_values)
                        + "\nFROM ltr_records"
                    )
                    connection.exec_driver_sql("DROP TABLE ltr_records")
                    connection.exec_driver_sql("ALTER TABLE ltr_records_new RENAME TO ltr_records")
                finally:
                    connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            else:
                column_defs = {
                    "is_current_owner": "BOOLEAN NOT NULL DEFAULT 1",
                    "superseded_at": "VARCHAR(64)",
                    "superseded_by_ltr_id": "VARCHAR(64)",
                    "superseded_reason": "TEXT",
                    "owner_version": "INTEGER NOT NULL DEFAULT 1",
                }
                for column, definition in column_defs.items():
                    if column in columns:
                        continue
                    connection.exec_driver_sql(
                        f"ALTER TABLE ltr_records ADD COLUMN {column} {definition}"
                    )

            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS ix_ltr_records_project_id "
                "ON ltr_records(project_id)"
            )
            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS ix_ltr_records_ltr_number "
                "ON ltr_records(ltr_number)"
            )
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_ltr_records_current_owner_ltr_number "
                "ON ltr_records(ltr_number) "
                "WHERE status = 'registered' AND is_current_owner = 1"
            )

        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS ltr_duplicate_resolution_tokens (
                token_id VARCHAR(64) NOT NULL,
                ltr_number VARCHAR(128) NOT NULL,
                existing_ltr_id VARCHAR(64) NOT NULL,
                existing_project_id VARCHAR(64) NOT NULL,
                current_case_id VARCHAR(64) NOT NULL,
                current_project_id VARCHAR(64) NOT NULL,
                conflict_fingerprint VARCHAR(128) NOT NULL,
                workbook_fingerprint VARCHAR(128),
                expires_at VARCHAR(64) NOT NULL,
                used_at VARCHAR(64),
                created_at VARCHAR(64) NOT NULL,
                created_by VARCHAR(255),
                metadata_json TEXT,
                PRIMARY KEY (token_id)
            )
            """
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_ltr_duplicate_resolution_tokens_ltr_number "
            "ON ltr_duplicate_resolution_tokens(ltr_number)"
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS ltr_association_events (
                event_id VARCHAR(64) NOT NULL,
                ltr_number VARCHAR(128) NOT NULL,
                event_type VARCHAR(128) NOT NULL,
                old_ltr_id VARCHAR(64),
                old_project_id VARCHAR(64),
                new_ltr_id VARCHAR(64),
                new_project_id VARCHAR(64),
                operator VARCHAR(255),
                reason TEXT NOT NULL,
                token_id VARCHAR(64),
                created_at VARCHAR(64) NOT NULL,
                metadata_json TEXT,
                PRIMARY KEY (event_id)
            )
            """
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_ltr_association_events_ltr_number "
            "ON ltr_association_events(ltr_number)"
        )
