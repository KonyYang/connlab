"""Idempotent additive schema registration for contact-measurement authority."""

from __future__ import annotations

import re

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


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

_REQUIRED_INDEXES = {
    "measurement_plan_revisions": {
        "uq_measurement_plan_confirmed_per_root",
        "uq_measurement_plan_editable_per_root",
    },
    "measurement_plan_target_snapshots": {"uq_measurement_plan_target_key"},
    "measurement_plan_impacts": {"uq_measurement_plan_impact_identity"},
}

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
    """Fail clearly when an existing authority table is incompatible."""
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
    for table_name, required_indexes in _REQUIRED_INDEXES.items():
        indexes = {item["name"] for item in inspector.get_indexes(table_name)}
        indexes.update(
            item["name"] for item in inspector.get_unique_constraints(table_name)
        )
        if required_indexes - indexes:
            raise RuntimeError(
                "Contact measurement plan authority schema is incompatible: "
                f"{table_name} is missing required indexes."
            )
    for table_name, required_checks in _REQUIRED_CHECKS.items():
        checks = {item.get("name") for item in inspector.get_check_constraints(table_name)}
        if required_checks - checks:
            raise RuntimeError(
                "Contact measurement plan authority schema is incompatible: "
                f"{table_name} is missing required checks."
            )
    with engine.connect() as connection:
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
        for index_name, predicate in (
            ("uq_measurement_plan_confirmed_per_root", "state = 'confirmed'"),
            ("uq_measurement_plan_editable_per_root", "state IN ('draft', 'needs_review')"),
        ):
            _validate_partial_index_shape(connection, index_name, predicate)
        _validate_unique_index_shape(
            connection,
            "measurement_plan_target_snapshots",
            ("measurement_plan_revision_id", "stable_target_key"),
        )
        _validate_unique_index_shape(
            connection,
            "measurement_plan_impacts",
            ("editable_revision_id", "impact_identity_key"),
        )


def _validate_unique_index_shape(connection, table_name: str, columns: tuple[str, ...]) -> None:
    """Require one exact full unique index, not merely a same-named SQLite object."""
    indexes = connection.exec_driver_sql(f"PRAGMA index_list({table_name})").all()
    for row in indexes:
        name, unique, partial = str(row[1]), bool(row[2]), bool(row[4])
        if not unique or partial:
            continue
        actual_columns = tuple(
            str(item[2])
            for item in connection.exec_driver_sql(f"PRAGMA index_info({name})").all()
        )
        if actual_columns == columns:
            return
    raise RuntimeError("authority_corrupt: existing authority unique-index shape is incompatible.")


def _validate_partial_index_shape(connection, index_name: str, predicate: str) -> None:
    """Require a unique single-root partial index with the exact canonical WHERE."""
    table = "measurement_plan_revisions"
    row = next(
        (item for item in connection.exec_driver_sql(f"PRAGMA index_list({table})").all() if str(item[1]) == index_name),
        None,
    )
    if row is None or not bool(row[2]) or not bool(row[4]):
        raise RuntimeError("authority_corrupt: existing authority partial-index shape is incompatible.")
    columns = tuple(
        str(item[2])
        for item in connection.exec_driver_sql(f"PRAGMA index_info({index_name})").all()
    )
    index_sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='index' AND name=?",
        (index_name,),
    ).scalar_one_or_none()
    actual_predicate = _where_predicate(index_sql or "")
    if columns != ("measurement_plan_root_id",) or _canonical_sql(predicate) != _canonical_sql(actual_predicate):
        raise RuntimeError("authority_corrupt: existing authority partial-index shape is incompatible.")


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
