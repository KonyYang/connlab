from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from backend.infrastructure.storage.matrix_identity_integrity_audit import (
    audit_matrix_identity_database,
)


def test_audit_reports_duplicate_draft_group_keys_without_modifying_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.execute(
            "INSERT INTO project_matrix_draft_records VALUES (?, ?, ?, ?)",
            ("draft-1", "project-1", "draft", "2026-09-16T00:00:00Z"),
        )
        connection.executemany(
            "INSERT INTO project_matrix_draft_groups VALUES (?, ?, ?, ?, ?)",
            (
                ("group-1", "draft-1", 1, "manual-group-1", "Group 1"),
                ("group-2", "draft-1", 2, "manual-group-1", "Group 2"),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    before = hashlib.sha256(database_path.read_bytes()).hexdigest()

    report = audit_matrix_identity_database(database_path)

    after = hashlib.sha256(database_path.read_bytes()).hexdigest()
    assert after == before
    assert report.database_path == database_path.resolve()
    assert report.counts.draft_records == 1
    assert report.counts.draft_groups == 2
    assert report.finding_counts == {"error": 1, "warning": 0}
    assert report.findings[0].code == "DRAFT_DUPLICATE_GROUP_KEY"
    assert report.findings[0].project_id == "project-1"
    assert report.findings[0].aggregate_id == "draft-1"
    assert report.findings[0].identity == "manual-group-1"


def test_audit_treats_valid_superseded_authority_as_retained_history_not_damage(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.executemany(
            "INSERT INTO confirmed_matrix_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                ("confirmed-1", "project-1", "draft-1", 1, 0, "superseded", "confirmed-2"),
                ("confirmed-2", "project-1", "draft-2", 2, 1, "confirmed", None),
            ),
        )
        connection.executemany(
            "INSERT INTO confirmed_matrix_groups VALUES (?, ?, ?, ?)",
            (
                ("confirmed-group-1", "confirmed-1", 1, "group-a"),
                ("confirmed-group-2", "confirmed-2", 1, "group-a"),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    report = audit_matrix_identity_database(database_path)

    assert report.counts.confirmed_versions == 2
    assert report.counts.active_confirmed_versions == 1
    assert report.counts.retained_confirmed_history_versions == 1
    assert report.findings == ()


def test_audit_reports_multiple_editable_drafts_for_one_project(tmp_path: Path) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.executemany(
            "INSERT INTO project_matrix_draft_records VALUES (?, ?, ?, ?)",
            (
                ("draft-1", "project-1", "draft", "2026-09-15T00:00:00Z"),
                ("draft-2", "project-1", "draft", "2026-09-16T00:00:00Z"),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    report = audit_matrix_identity_database(database_path)

    assert report.counts.editable_draft_records == 2
    assert [finding.code for finding in report.findings] == [
        "DRAFT_MULTIPLE_EDITABLE_PER_PROJECT"
    ]
    assert report.findings[0].project_id == "project-1"
    assert report.findings[0].occurrence_count == 2


def test_audit_reports_duplicate_group_identity_in_active_confirmed_authority(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.execute(
            "INSERT INTO confirmed_matrix_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("confirmed-1", "project-1", "draft-1", 1, 1, "confirmed", None),
        )
        connection.executemany(
            "INSERT INTO confirmed_matrix_groups VALUES (?, ?, ?, ?)",
            (
                ("confirmed-group-1", "confirmed-1", 1, "group-a"),
                ("confirmed-group-2", "confirmed-1", 2, "group-a"),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    report = audit_matrix_identity_database(database_path)

    assert [finding.code for finding in report.findings] == [
        "CONFIRMED_DUPLICATE_GROUP_KEY"
    ]
    assert report.findings[0].severity == "error"
    assert report.findings[0].aggregate_id == "confirmed-1"


def test_audit_reports_multiple_active_authorities_for_one_project(tmp_path: Path) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.executemany(
            "INSERT INTO confirmed_matrix_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                ("confirmed-1", "project-1", "draft-1", 1, 1, "confirmed", None),
                ("confirmed-2", "project-1", "draft-2", 2, 1, "confirmed", None),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    report = audit_matrix_identity_database(database_path)

    assert [finding.code for finding in report.findings] == [
        "CONFIRMED_MULTIPLE_ACTIVE_PER_PROJECT"
    ]
    assert report.findings[0].occurrence_count == 2


def test_audit_reports_draft_cells_with_missing_group_lineage(tmp_path: Path) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.execute(
            "INSERT INTO project_matrix_draft_records VALUES (?, ?, ?, ?)",
            ("draft-1", "project-1", "draft", "2026-09-16T00:00:00Z"),
        )
        connection.execute(
            "INSERT INTO project_matrix_draft_rows VALUES (?, ?, ?)",
            ("row-1", "draft-1", 1),
        )
        connection.execute(
            "INSERT INTO project_matrix_draft_cells VALUES (?, ?, ?, ?)",
            ("cell-1", "draft-1", "row-1", "missing-group"),
        )
        connection.commit()
    finally:
        connection.close()

    report = audit_matrix_identity_database(database_path)

    assert [finding.code for finding in report.findings] == [
        "DRAFT_CELL_ORPHAN_GROUP"
    ]
    assert report.findings[0].identity == "missing-group"


def test_audit_reports_sqlite_foreign_key_violations(tmp_path: Path) -> None:
    database_path = tmp_path / "matrix.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        _create_minimal_matrix_schema(connection)
        connection.execute(
            """
            CREATE TABLE project_matrix_draft_step_quantities (
                draft_step_quantity_id TEXT PRIMARY KEY,
                draft_group_id TEXT NOT NULL,
                FOREIGN KEY(draft_group_id)
                    REFERENCES project_matrix_draft_groups(draft_group_id)
            )
            """
        )
        connection.execute(
            "INSERT INTO project_matrix_draft_step_quantities VALUES (?, ?)",
            ("quantity-1", "missing-group"),
        )
        connection.commit()
    finally:
        connection.close()

    report = audit_matrix_identity_database(database_path)

    assert [finding.code for finding in report.findings] == [
        "SQLITE_FOREIGN_KEY_VIOLATION"
    ]
    assert report.findings[0].aggregate_id == "project_matrix_draft_step_quantities"
    assert report.findings[0].identity == "project_matrix_draft_groups"


def _create_minimal_matrix_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE project_matrix_draft_records (
            project_matrix_draft_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            status TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE project_matrix_draft_groups (
            draft_group_id TEXT PRIMARY KEY,
            project_matrix_draft_id TEXT NOT NULL,
            group_order INTEGER NOT NULL,
            group_key TEXT NOT NULL,
            group_label TEXT NOT NULL
        );
        CREATE TABLE project_matrix_draft_rows (
            draft_row_id TEXT PRIMARY KEY,
            project_matrix_draft_id TEXT NOT NULL,
            row_order INTEGER NOT NULL
        );
        CREATE TABLE project_matrix_draft_cells (
            draft_cell_id TEXT PRIMARY KEY,
            project_matrix_draft_id TEXT NOT NULL,
            draft_row_id TEXT NOT NULL,
            draft_group_id TEXT NOT NULL
        );
        CREATE TABLE confirmed_matrix_versions (
            confirmed_matrix_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            project_matrix_draft_id TEXT NOT NULL,
            confirmed_revision INTEGER NOT NULL,
            is_active_authority INTEGER NOT NULL,
            status TEXT NOT NULL,
            superseded_by_confirmed_matrix_id TEXT
        );
        CREATE TABLE confirmed_matrix_groups (
            confirmed_group_id TEXT PRIMARY KEY,
            confirmed_matrix_id TEXT NOT NULL,
            group_order INTEGER NOT NULL,
            group_key TEXT NOT NULL
        );
        CREATE TABLE confirmed_matrix_rows (
            confirmed_row_id TEXT PRIMARY KEY,
            confirmed_matrix_id TEXT NOT NULL,
            row_order INTEGER NOT NULL
        );
        CREATE TABLE confirmed_matrix_cells (
            confirmed_cell_id TEXT PRIMARY KEY,
            confirmed_matrix_id TEXT NOT NULL,
            confirmed_row_id TEXT NOT NULL,
            confirmed_group_id TEXT NOT NULL
        );
        """
    )
