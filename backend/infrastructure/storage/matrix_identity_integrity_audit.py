"""Read-only integrity audit for Matrix draft and confirmed authority identities."""

from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MatrixIdentityAuditCounts:
    draft_records: int
    draft_groups: int
    editable_draft_records: int
    confirmed_versions: int
    confirmed_groups: int
    active_confirmed_versions: int
    retained_confirmed_history_versions: int


@dataclass(frozen=True, slots=True)
class MatrixIdentityAuditFinding:
    code: str
    severity: str
    project_id: str | None
    aggregate_id: str
    identity: str
    occurrence_count: int
    message: str


@dataclass(frozen=True, slots=True)
class MatrixIdentityAuditReport:
    database_path: Path
    counts: MatrixIdentityAuditCounts
    findings: tuple[MatrixIdentityAuditFinding, ...]

    @property
    def finding_counts(self) -> dict[str, int]:
        return {
            severity: sum(1 for finding in self.findings if finding.severity == severity)
            for severity in ("error", "warning")
        }


def audit_matrix_identity_database(database_path: Path) -> MatrixIdentityAuditReport:
    """Inspect Matrix identity integrity without opening a writable SQLite connection."""

    resolved_path = database_path.resolve(strict=True)
    connection = sqlite3.connect(
        f"file:{resolved_path.as_posix()}?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        counts = MatrixIdentityAuditCounts(
            draft_records=_table_count(connection, "project_matrix_draft_records"),
            draft_groups=_table_count(connection, "project_matrix_draft_groups"),
            editable_draft_records=_where_count(
                connection,
                "project_matrix_draft_records",
                "status = 'draft'",
            ),
            confirmed_versions=_table_count(connection, "confirmed_matrix_versions"),
            confirmed_groups=_table_count(connection, "confirmed_matrix_groups"),
            active_confirmed_versions=_where_count(
                connection,
                "confirmed_matrix_versions",
                "is_active_authority = 1",
            ),
            retained_confirmed_history_versions=_where_count(
                connection,
                "confirmed_matrix_versions",
                "is_active_authority = 0",
            ),
        )
        findings = tuple(
            [
                *_duplicate_draft_group_key_findings(connection),
                *_multiple_editable_draft_findings(connection),
                *_duplicate_confirmed_group_key_findings(connection),
                *_multiple_active_authority_findings(connection),
                *_draft_cell_orphan_findings(connection),
                *_sqlite_foreign_key_findings(connection),
            ]
        )
    finally:
        connection.close()
    return MatrixIdentityAuditReport(
        database_path=resolved_path,
        counts=counts,
        findings=findings,
    )


def _table_count(connection: sqlite3.Connection, table_name: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
    return int(row["count"])


def _where_count(
    connection: sqlite3.Connection,
    table_name: str,
    where_clause: str,
) -> int:
    row = connection.execute(
        f"SELECT COUNT(*) AS count FROM {table_name} WHERE {where_clause}"
    ).fetchone()
    return int(row["count"])


def _duplicate_draft_group_key_findings(
    connection: sqlite3.Connection,
) -> list[MatrixIdentityAuditFinding]:
    rows = connection.execute(
        """
        SELECT
            draft.project_id,
            groups.project_matrix_draft_id,
            groups.group_key,
            COUNT(*) AS occurrence_count
        FROM project_matrix_draft_groups AS groups
        JOIN project_matrix_draft_records AS draft
          ON draft.project_matrix_draft_id = groups.project_matrix_draft_id
        GROUP BY
            draft.project_id,
            groups.project_matrix_draft_id,
            groups.group_key
        HAVING COUNT(*) > 1
        ORDER BY draft.project_id, groups.project_matrix_draft_id, groups.group_key
        """
    ).fetchall()
    return [
        MatrixIdentityAuditFinding(
            code="DRAFT_DUPLICATE_GROUP_KEY",
            severity="error",
            project_id=str(row["project_id"]),
            aggregate_id=str(row["project_matrix_draft_id"]),
            identity=str(row["group_key"]),
            occurrence_count=int(row["occurrence_count"]),
            message="One Matrix draft contains more than one group with the same identity.",
        )
        for row in rows
    ]


def _multiple_editable_draft_findings(
    connection: sqlite3.Connection,
) -> list[MatrixIdentityAuditFinding]:
    rows = connection.execute(
        """
        SELECT project_id, COUNT(*) AS occurrence_count
        FROM project_matrix_draft_records
        WHERE status = 'draft'
        GROUP BY project_id
        HAVING COUNT(*) > 1
        ORDER BY project_id
        """
    ).fetchall()
    return [
        MatrixIdentityAuditFinding(
            code="DRAFT_MULTIPLE_EDITABLE_PER_PROJECT",
            severity="error",
            project_id=str(row["project_id"]),
            aggregate_id=str(row["project_id"]),
            identity="draft",
            occurrence_count=int(row["occurrence_count"]),
            message="One Project has more than one editable Matrix working draft.",
        )
        for row in rows
    ]


def _duplicate_confirmed_group_key_findings(
    connection: sqlite3.Connection,
) -> list[MatrixIdentityAuditFinding]:
    rows = connection.execute(
        """
        SELECT
            version.project_id,
            version.is_active_authority,
            groups.confirmed_matrix_id,
            groups.group_key,
            COUNT(*) AS occurrence_count
        FROM confirmed_matrix_groups AS groups
        JOIN confirmed_matrix_versions AS version
          ON version.confirmed_matrix_id = groups.confirmed_matrix_id
        GROUP BY
            version.project_id,
            version.is_active_authority,
            groups.confirmed_matrix_id,
            groups.group_key
        HAVING COUNT(*) > 1
        ORDER BY version.project_id, groups.confirmed_matrix_id, groups.group_key
        """
    ).fetchall()
    return [
        MatrixIdentityAuditFinding(
            code="CONFIRMED_DUPLICATE_GROUP_KEY",
            severity="error" if bool(row["is_active_authority"]) else "warning",
            project_id=str(row["project_id"]),
            aggregate_id=str(row["confirmed_matrix_id"]),
            identity=str(row["group_key"]),
            occurrence_count=int(row["occurrence_count"]),
            message=(
                "One confirmed Matrix version contains more than one group with the "
                "same identity."
            ),
        )
        for row in rows
    ]


def _multiple_active_authority_findings(
    connection: sqlite3.Connection,
) -> list[MatrixIdentityAuditFinding]:
    rows = connection.execute(
        """
        SELECT project_id, COUNT(*) AS occurrence_count
        FROM confirmed_matrix_versions
        WHERE is_active_authority = 1
        GROUP BY project_id
        HAVING COUNT(*) > 1
        ORDER BY project_id
        """
    ).fetchall()
    return [
        MatrixIdentityAuditFinding(
            code="CONFIRMED_MULTIPLE_ACTIVE_PER_PROJECT",
            severity="error",
            project_id=str(row["project_id"]),
            aggregate_id=str(row["project_id"]),
            identity="active-authority",
            occurrence_count=int(row["occurrence_count"]),
            message="One Project has more than one active confirmed Matrix authority.",
        )
        for row in rows
    ]


def _draft_cell_orphan_findings(
    connection: sqlite3.Connection,
) -> list[MatrixIdentityAuditFinding]:
    findings: list[MatrixIdentityAuditFinding] = []
    group_rows = connection.execute(
        """
        SELECT
            draft.project_id,
            cell.project_matrix_draft_id,
            cell.draft_group_id,
            COUNT(*) AS occurrence_count
        FROM project_matrix_draft_cells AS cell
        JOIN project_matrix_draft_records AS draft
          ON draft.project_matrix_draft_id = cell.project_matrix_draft_id
        LEFT JOIN project_matrix_draft_groups AS groups
          ON groups.project_matrix_draft_id = cell.project_matrix_draft_id
         AND groups.draft_group_id = cell.draft_group_id
        WHERE groups.draft_group_id IS NULL
        GROUP BY draft.project_id, cell.project_matrix_draft_id, cell.draft_group_id
        ORDER BY draft.project_id, cell.project_matrix_draft_id, cell.draft_group_id
        """
    ).fetchall()
    findings.extend(
        MatrixIdentityAuditFinding(
            code="DRAFT_CELL_ORPHAN_GROUP",
            severity="error",
            project_id=str(row["project_id"]),
            aggregate_id=str(row["project_matrix_draft_id"]),
            identity=str(row["draft_group_id"]),
            occurrence_count=int(row["occurrence_count"]),
            message="Draft Matrix cells reference a group outside their draft aggregate.",
        )
        for row in group_rows
    )
    row_rows = connection.execute(
        """
        SELECT
            draft.project_id,
            cell.project_matrix_draft_id,
            cell.draft_row_id,
            COUNT(*) AS occurrence_count
        FROM project_matrix_draft_cells AS cell
        JOIN project_matrix_draft_records AS draft
          ON draft.project_matrix_draft_id = cell.project_matrix_draft_id
        LEFT JOIN project_matrix_draft_rows AS rows
          ON rows.project_matrix_draft_id = cell.project_matrix_draft_id
         AND rows.draft_row_id = cell.draft_row_id
        WHERE rows.draft_row_id IS NULL
        GROUP BY draft.project_id, cell.project_matrix_draft_id, cell.draft_row_id
        ORDER BY draft.project_id, cell.project_matrix_draft_id, cell.draft_row_id
        """
    ).fetchall()
    findings.extend(
        MatrixIdentityAuditFinding(
            code="DRAFT_CELL_ORPHAN_ROW",
            severity="error",
            project_id=str(row["project_id"]),
            aggregate_id=str(row["project_matrix_draft_id"]),
            identity=str(row["draft_row_id"]),
            occurrence_count=int(row["occurrence_count"]),
            message="Draft Matrix cells reference a row outside their draft aggregate.",
        )
        for row in row_rows
    )
    return findings


def _sqlite_foreign_key_findings(
    connection: sqlite3.Connection,
) -> list[MatrixIdentityAuditFinding]:
    grouped = Counter(
        (str(row["table"]), str(row["parent"]))
        for row in connection.execute("PRAGMA foreign_key_check").fetchall()
    )
    return [
        MatrixIdentityAuditFinding(
            code="SQLITE_FOREIGN_KEY_VIOLATION",
            severity="error",
            project_id=None,
            aggregate_id=table_name,
            identity=parent_table,
            occurrence_count=occurrence_count,
            message=(
                f"{occurrence_count} row(s) in {table_name} reference missing "
                f"records in {parent_table}."
            ),
        )
        for (table_name, parent_table), occurrence_count in sorted(grouped.items())
    ]
