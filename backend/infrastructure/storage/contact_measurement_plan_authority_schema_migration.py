"""Idempotent additive schema registration for contact-measurement authority."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError


_REQUIRED_COLUMNS = {
    "measurement_plan_roots": {
        "measurement_plan_root_id",
        "project_id",
        "active_confirmed_revision_id",
        "editable_revision_id",
        "created_at",
        "updated_at",
    },
    "measurement_plan_revisions": {
        "measurement_plan_revision_id",
        "measurement_plan_root_id",
        "revision_sequence",
        "state",
        "revision_fingerprint",
        "base_confirmed_matrix_id",
        "matrix_binding_fingerprint",
    },
    "measurement_plan_target_snapshots": {
        "measurement_plan_target_snapshot_id",
        "measurement_plan_revision_id",
        "stable_target_key",
        "confirmed_matrix_id",
        "contact_kind",
        "readings_per_sample",
    },
    "measurement_plan_family_snapshots": {
        "measurement_plan_family_snapshot_id",
        "measurement_plan_target_snapshot_id",
        "family_id",
        "count_per_sample",
    },
    "measurement_plan_impacts": {
        "measurement_plan_impact_id",
        "measurement_plan_root_id",
        "editable_revision_id",
        "impact_subject_key",
        "impact_identity_key",
    },
    "measurement_plan_audits": {
        "measurement_plan_audit_id",
        "measurement_plan_root_id",
        "action",
        "actor",
        "occurred_at",
    },
}

@dataclass(frozen=True)
class _SemanticIndex:
    name: str
    table: str
    columns: tuple[str, ...]
    predicate: str | None = None


_SEMANTIC_INDEXES = (
    _SemanticIndex(
        "uq_measurement_plan_confirmed_per_root",
        "measurement_plan_revisions",
        ("measurement_plan_root_id",),
        "state = 'confirmed'",
    ),
    _SemanticIndex(
        "uq_measurement_plan_editable_per_root",
        "measurement_plan_revisions",
        ("measurement_plan_root_id",),
        "state IN ('draft', 'needs_review')",
    ),
    _SemanticIndex(
        "uq_measurement_plan_target_key",
        "measurement_plan_target_snapshots",
        ("measurement_plan_revision_id", "stable_target_key"),
    ),
    _SemanticIndex(
        "uq_measurement_plan_impact_identity",
        "measurement_plan_impacts",
        ("editable_revision_id", "impact_identity_key"),
    ),
)

_REQUIRED_CHECKS = {
    "measurement_plan_target_snapshots": {
        "ck_measurement_plan_group_anchor_xor",
        "ck_measurement_plan_row_anchor_xor",
        "ck_measurement_plan_target_key_shape",
    },
    "measurement_plan_impacts": {
        "ck_measurement_plan_impact_subject_shape",
        "ck_measurement_plan_impact_identity_shape",
    },
}

_REQUIRED_FOREIGN_KEY_TARGETS = {
    "measurement_plan_roots": {"projects", "measurement_plan_revisions"},
    "measurement_plan_revisions": {"measurement_plan_roots", "confirmed_matrix_versions"},
    "measurement_plan_target_snapshots": {"measurement_plan_revisions", "confirmed_matrix_versions"},
    "measurement_plan_family_snapshots": {"measurement_plan_target_snapshots"},
    "measurement_plan_impacts": {"measurement_plan_roots", "measurement_plan_revisions"},
    "measurement_plan_audits": {"measurement_plan_roots", "measurement_plan_revisions"},
}

_REQUIRED_FOREIGN_KEY_SHAPES = {
    "measurement_plan_roots": {
        ("project_id", "projects", "project_id"),
        ("active_confirmed_revision_id", "measurement_plan_revisions", "measurement_plan_revision_id"),
        ("editable_revision_id", "measurement_plan_revisions", "measurement_plan_revision_id"),
    },
    "measurement_plan_revisions": {
        ("measurement_plan_root_id", "measurement_plan_roots", "measurement_plan_root_id"),
        ("parent_revision_id", "measurement_plan_revisions", "measurement_plan_revision_id"),
        ("base_confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"),
    },
    "measurement_plan_target_snapshots": {
        ("measurement_plan_revision_id", "measurement_plan_revisions", "measurement_plan_revision_id"),
        ("confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"),
    },
    "measurement_plan_family_snapshots": {("measurement_plan_target_snapshot_id", "measurement_plan_target_snapshots", "measurement_plan_target_snapshot_id")},
    "measurement_plan_impacts": {("measurement_plan_root_id", "measurement_plan_roots", "measurement_plan_root_id"), ("editable_revision_id", "measurement_plan_revisions", "measurement_plan_revision_id")},
    "measurement_plan_audits": {("measurement_plan_root_id", "measurement_plan_roots", "measurement_plan_root_id"), ("measurement_plan_revision_id", "measurement_plan_revisions", "measurement_plan_revision_id")},
}

_REQUIRED_CHECK_EXPRESSIONS = {
    "measurement_plan_target_snapshots": (
        ("ck_measurement_plan_group_anchor_xor", "(source_group_snapshot_id IS NOT NULL AND length(trim(source_group_snapshot_id)) > 0 AND manual_group_anchor_id IS NULL) OR (source_group_snapshot_id IS NULL AND manual_group_anchor_id IS NOT NULL AND length(trim(manual_group_anchor_id)) > 0)"),
        ("ck_measurement_plan_row_anchor_xor", "(source_row_snapshot_id IS NOT NULL AND length(trim(source_row_snapshot_id)) > 0 AND manual_row_anchor_id IS NULL) OR (source_row_snapshot_id IS NULL AND manual_row_anchor_id IS NOT NULL AND length(trim(manual_row_anchor_id)) > 0)"),
        ("ck_measurement_plan_target_key_shape", "stable_target_key LIKE 'cmp-target:v1|%'"),
    ),
    "measurement_plan_impacts": (
        ("ck_measurement_plan_impact_subject_shape", "impact_subject_key LIKE 'cmp-target:v1|%' OR impact_subject_key LIKE 'cmp-candidate:v1|%'"),
        ("ck_measurement_plan_impact_identity_shape", "impact_identity_key LIKE 'cmp-impact:v1|%'"),
    ),
}


def migrate_contact_measurement_plan_authority_schema(engine: Engine) -> None:
    """Bootstrap missing SQLite authority indexes without changing authority data."""
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    missing_tables = set(_REQUIRED_COLUMNS) - names
    if missing_tables:
        raise RuntimeError("Contact measurement plan authority schema is incomplete.")
    for table_name, required_columns in _REQUIRED_COLUMNS.items():
        columns = {
            column["name"]
            for column in inspector.get_columns(table_name)
        }
        missing_columns = required_columns - columns
        if missing_columns:
            raise RuntimeError(
                "Contact measurement plan authority schema is incompatible: "
                f"{table_name} is missing {', '.join(sorted(missing_columns))}."
            )
    for table_name, required_checks in _REQUIRED_CHECKS.items():
        checks = {item.get("name") for item in inspector.get_check_constraints(table_name)}
        if required_checks - checks:
            raise RuntimeError(
                "Contact measurement plan authority schema is incompatible: "
                f"{table_name} is missing required checks."
            )
    with engine.connect() as connection:
        _validate_identity_columns_non_null(connection)
        for table_name, expected_targets in _REQUIRED_FOREIGN_KEY_TARGETS.items():
            foreign_keys = connection.exec_driver_sql(
                f"PRAGMA foreign_key_list({table_name})"
            ).all()
            targets = {str(row[2]) for row in foreign_keys}
            if not expected_targets <= targets:
                raise RuntimeError(
                    "authority_corrupt: existing authority foreign-key shape is incompatible."
                )
            actual_shapes = {(str(row[3]), str(row[2]), str(row[4])) for row in foreign_keys}
            if _REQUIRED_FOREIGN_KEY_SHAPES[table_name] != actual_shapes or any(
                str(row[5]).upper() != "NO ACTION"
                or str(row[6]).upper() != "NO ACTION"
                or str(row[7]).upper() != "NONE"
                for row in foreign_keys
            ):
                raise RuntimeError(
                    "authority_corrupt: existing authority foreign-key shape is incompatible."
                )
        for table_name, required_checks in _REQUIRED_CHECK_EXPRESSIONS.items():
            actual_checks = {
                str(item.get("name")): _canonical_sql(str(item.get("sqltext") or ""))
                for item in inspector.get_check_constraints(table_name)
            }
            if any(
                actual_checks.get(name) != _canonical_sql(expression)
                for name, expression in required_checks
            ):
                raise RuntimeError(
                    "authority_corrupt: existing authority CHECK shape is incompatible."
                )
        missing = _missing_semantic_indexes(connection)
        _preflight_missing_indexes(connection, missing)

    if not missing:
        return
    with engine.connect() as connection:
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        except OperationalError as exc:
            if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                raise RuntimeError(
                    "Contact measurement plan authority schema bootstrap is locked."
                ) from exc
            raise
        try:
            missing = _missing_semantic_indexes(connection)
            _preflight_missing_indexes(connection, missing)
            for index in missing:
                connection.exec_driver_sql(_create_index_sql(index))
            if _missing_semantic_indexes(connection):
                raise RuntimeError("authority_corrupt: authority index bootstrap did not verify.")
        except BaseException:
            connection.rollback()
            raise
        connection.commit()


def _validate_identity_columns_non_null(connection) -> None:
    for index in _SEMANTIC_INDEXES:
        columns = {
            str(row[1]): bool(row[3])
            for row in connection.exec_driver_sql(f"PRAGMA table_info({index.table})").all()
        }
        if any(not columns.get(column, False) for column in index.columns):
            raise RuntimeError("authority_corrupt: authority identity columns must be non-null.")


def _missing_semantic_indexes(connection) -> tuple[_SemanticIndex, ...]:
    missing: list[_SemanticIndex] = []
    for index in _SEMANTIC_INDEXES:
        matches = _find_semantic_indexes(connection, index)
        canonical = _index_row(connection, index.table, index.name)
        if canonical is not None and index.name not in matches:
            raise RuntimeError("authority_corrupt: existing authority unique-index shape is incompatible.")
        if not matches:
            missing.append(index)
    return tuple(missing)


def _find_semantic_indexes(connection, expected: _SemanticIndex) -> set[str]:
    matches: set[str] = set()
    for row in connection.exec_driver_sql(f"PRAGMA index_list({expected.table})").all():
        name, unique, partial = str(row[1]), bool(row[2]), bool(row[4])
        columns = tuple(
            str(item[2])
            for item in connection.exec_driver_sql(f"PRAGMA index_info({name})").all()
        )
        predicate = _index_predicate(connection, name) if partial else None
        exact = (
            unique
            and columns == expected.columns
            and partial is (expected.predicate is not None)
            and (expected.predicate is None or _canonical_sql(predicate or "") == _canonical_sql(expected.predicate))
        )
        if exact:
            matches.add(name)
        elif name == expected.name:
            raise RuntimeError("authority_corrupt: existing authority unique-index shape is incompatible.")
    return matches


def _index_row(connection, table_name: str, index_name: str):
    return next(
        (
            row
            for row in connection.exec_driver_sql(f"PRAGMA index_list({table_name})").all()
            if str(row[1]) == index_name
        ),
        None,
    )


def _index_predicate(connection, index_name: str) -> str:
    index_sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='index' AND name=?",
        (index_name,),
    ).scalar_one_or_none()
    return _where_predicate(index_sql or "")


def _preflight_missing_indexes(connection, missing: tuple[_SemanticIndex, ...]) -> None:
    for index in missing:
        column_list = ", ".join(index.columns)
        null_filter = " OR ".join(f"{column} IS NULL" for column in index.columns)
        if connection.exec_driver_sql(
            f"SELECT 1 FROM {index.table} WHERE {null_filter} LIMIT 1"
        ).first() is not None:
            raise RuntimeError("authority_corrupt: authority identity contains null values.")
        where = f"WHERE {index.predicate}" if index.predicate else ""
        duplicate = connection.exec_driver_sql(
            f"SELECT 1 FROM {index.table} {where} GROUP BY {column_list} HAVING COUNT(*) > 1 LIMIT 1"
        ).first()
        if duplicate is not None:
            raise RuntimeError("authority_corrupt: authority unique-index preflight found duplicates.")


def _create_index_sql(index: _SemanticIndex) -> str:
    predicate = f" WHERE {index.predicate}" if index.predicate else ""
    return f"CREATE UNIQUE INDEX {index.name} ON {index.table} ({', '.join(index.columns)}){predicate}"


def _canonical_sql(value: str) -> str:
    """Normalize SQL tokens without altering boolean grouping or operator meaning."""
    tokens = re.findall(
        r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`[^`]*`|\[[^\]]*\]|<>|!=|<=|>=|[(),]|=|<|>|\b\w+\b",
        value.lower(),
    )
    normalized = [
        token[1:-1] if token[:1] in {'"', '`', '['} and token[-1:] in {'"', '`', ']'} else token
        for token in tokens
    ]
    while _is_wrapped(normalized):
        normalized = normalized[1:-1]
    return " ".join(normalized)


def _where_predicate(index_sql: str) -> str:
    match = re.search(r"\bwhere\b(?P<predicate>.+)$", index_sql, flags=re.IGNORECASE)
    return match.group("predicate") if match else ""


def _is_wrapped(tokens: list[str]) -> bool:
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        return False
    depth = 0
    for index, token in enumerate(tokens):
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
        if depth == 0 and index != len(tokens) - 1:
            return False
    return depth == 0
