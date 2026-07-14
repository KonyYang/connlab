"""Fail-closed SQLite shape validation for additive Point Profile authority."""

from __future__ import annotations

import re


_TABLE_COLUMNS = {
    "contact_point_profile_roots": {
        "contact_point_profile_root_id": ("VARCHAR(64)", 1, 1), "project_id": ("VARCHAR(64)", 1, 0),
        "active_confirmed_revision_id": ("VARCHAR(64)", 0, 0), "editable_revision_id": ("VARCHAR(64)", 0, 0),
        "created_at": ("VARCHAR(64)", 1, 0), "updated_at": ("VARCHAR(64)", 1, 0),
    },
    "contact_point_profile_revisions": {
        "contact_point_profile_revision_id": ("VARCHAR(64)", 1, 1), "contact_point_profile_root_id": ("VARCHAR(64)", 1, 0),
        "revision_sequence": ("INTEGER", 1, 0), "parent_revision_id": ("VARCHAR(64)", 0, 0), "state": ("VARCHAR(32)", 1, 0),
        "revision_fingerprint": ("VARCHAR(128)", 1, 0), "bootstrap_provenance": ("TEXT", 0, 0), "created_by": ("VARCHAR(255)", 1, 0),
        "created_at": ("VARCHAR(64)", 1, 0), "updated_at": ("VARCHAR(64)", 1, 0), "confirmed_by": ("VARCHAR(255)", 0, 0),
        "confirmed_at": ("VARCHAR(64)", 0, 0), "superseded_at": ("VARCHAR(64)", 0, 0), "superseded_reason": ("TEXT", 0, 0),
    },
    "contact_point_profile_categories": {
        "contact_point_profile_category_snapshot_id": ("VARCHAR(64)", 1, 1), "contact_point_profile_revision_id": ("VARCHAR(64)", 1, 0),
        "category_id": ("VARCHAR(64)", 1, 0), "category_ordinal": ("INTEGER", 1, 0), "label": ("TEXT", 1, 0),
        "normalized_label_key": ("TEXT", 1, 0), "count_per_sample": ("INTEGER", 1, 0), "record_prefix": ("VARCHAR(64)", 1, 0),
        "normalized_prefix_key": ("VARCHAR(64)", 1, 0), "included": ("BOOLEAN", 1, 0),
        "point_expression": ("TEXT", 0, 0),
    },
}

_FOREIGN_KEYS = {
    "contact_point_profile_roots": {("project_id", "projects", "project_id"), ("active_confirmed_revision_id", "contact_point_profile_revisions", "contact_point_profile_revision_id"), ("editable_revision_id", "contact_point_profile_revisions", "contact_point_profile_revision_id")},
    "contact_point_profile_revisions": {("contact_point_profile_root_id", "contact_point_profile_roots", "contact_point_profile_root_id"), ("parent_revision_id", "contact_point_profile_revisions", "contact_point_profile_revision_id")},
    "contact_point_profile_categories": {("contact_point_profile_revision_id", "contact_point_profile_revisions", "contact_point_profile_revision_id")},
}

_UNIQUE_COLUMNS = {
    "contact_point_profile_roots": {("project_id",)},
    "contact_point_profile_revisions": {("contact_point_profile_root_id", "revision_sequence"), ("bootstrap_provenance",)},
    "contact_point_profile_categories": {("contact_point_profile_revision_id", "category_ordinal"), ("contact_point_profile_revision_id", "category_id")},
}

_PARTIAL_INDEXES = {
    "contact_point_profile_revisions": {
        "uq_contact_point_profile_confirmed_per_root": (("contact_point_profile_root_id",), "state = 'confirmed'"),
        "uq_contact_point_profile_editable_per_root": (("contact_point_profile_root_id",), "state = 'draft'"),
    },
    "contact_point_profile_categories": {
        "uq_contact_point_profile_included_label": (("contact_point_profile_revision_id", "normalized_label_key"), "included = 1"),
        "uq_contact_point_profile_included_prefix": (("contact_point_profile_revision_id", "normalized_prefix_key"), "included = 1"),
    },
}

_CHECKS = {
    "contact_point_profile_revisions": (("ck_contact_point_profile_revision_positive", "revision_sequence > 0"), ("ck_contact_point_profile_revision_state", "state IN ('draft','confirmed','superseded')")),
    "contact_point_profile_categories": (("ck_contact_point_profile_category_numbers", "category_ordinal >= 0 AND count_per_sample >= 0"), ("ck_contact_point_profile_included_count", "included = 0 OR count_per_sample > 0"), ("ck_contact_point_profile_point_expression_nonblank", "point_expression IS NULL OR length(trim(point_expression)) > 0")),
}


def migrate_contact_point_profile_schema(engine, *, allow_partial: bool = False) -> None:
    """Validate existing Point Profile structures; never repair incompatible tables."""
    if engine.dialect.name != "sqlite":
        return
    with engine.connect() as connection:
        names = {row[0] for row in connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").all()}
        existing = set(_TABLE_COLUMNS) & names
        if not existing:
            if allow_partial:
                return
            raise RuntimeError("authority_corrupt: Point Profile additive table was not registered.")
        if not allow_partial and existing != set(_TABLE_COLUMNS):
            raise RuntimeError("authority_corrupt: Point Profile additive table was not registered.")
        for table in existing:
            _validate_table(connection, table)


def bootstrap_contact_point_profile_schema(engine) -> None:
    """Create missing Point Profile objects only after all existing shapes pass."""
    if engine.dialect.name != "sqlite":
        return
    from backend.infrastructure.storage.models_contact_point_profile import (
        ContactPointProfileCategoryModel, ContactPointProfileRevisionModel, ContactPointProfileRootModel,
    )
    tables = [
        ContactPointProfileRootModel.__table__, ContactPointProfileRevisionModel.__table__,
        ContactPointProfileCategoryModel.__table__,
    ]
    with engine.connect() as connection:
        names = {row[0] for row in connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").all()}
        for table in tables:
            if table.name in names:
                _validate_existing_table(connection, table.name)
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            for table in tables:
                if table.name not in names:
                    table.create(connection, checkfirst=False)
            if "contact_point_profile_categories" in names and _is_v1_category_shape(connection):
                connection.exec_driver_sql(
                    "ALTER TABLE contact_point_profile_categories ADD COLUMN point_expression TEXT "
                    "CONSTRAINT ck_contact_point_profile_point_expression_nonblank "
                    "CHECK (point_expression IS NULL OR length(trim(point_expression)) > 0)"
                )
            for table in _TABLE_COLUMNS:
                _validate_table(connection, table)
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("authority_corrupt: Point Profile bootstrap failed.") from exc


def _validate_table(connection, table: str) -> None:
    columns = {str(row[1]): (str(row[2]).upper(), int(row[3]), int(row[5])) for row in connection.exec_driver_sql(f"PRAGMA table_info({table})").all()}
    if columns != _TABLE_COLUMNS[table]:
        _corrupt()
    foreign_keys = connection.exec_driver_sql(f"PRAGMA foreign_key_list({table})").all()
    actual_fks = {(str(row[3]), str(row[2]), str(row[4])) for row in foreign_keys}
    if actual_fks != _FOREIGN_KEYS[table] or any(str(row[5]).upper() != "NO ACTION" or str(row[6]).upper() != "NO ACTION" or str(row[7]).upper() != "NONE" for row in foreign_keys):
        _corrupt()
    sql = connection.exec_driver_sql("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).scalar_one_or_none() or ""
    normalized_sql = _canonical_expression(sql)
    if any(
        _canonical_expression(name) not in normalized_sql or _canonical_expression(check) not in normalized_sql
        for name, check in _CHECKS.get(table, ())
    ):
        _corrupt()
    _validate_indexes(connection, table)


def _validate_existing_table(connection, table: str) -> None:
    if table == "contact_point_profile_categories" and _is_v1_category_shape(connection):
        _validate_category_v1(connection)
        return
    _validate_table(connection, table)


def _is_v1_category_shape(connection) -> bool:
    columns = {str(row[1]) for row in connection.exec_driver_sql("PRAGMA table_info(contact_point_profile_categories)").all()}
    return columns == set(_TABLE_COLUMNS["contact_point_profile_categories"]) - {"point_expression"}


def _validate_category_v1(connection) -> None:
    expected = dict(_TABLE_COLUMNS["contact_point_profile_categories"])
    expected.pop("point_expression")
    columns = {str(row[1]): (str(row[2]).upper(), int(row[3]), int(row[5])) for row in connection.exec_driver_sql("PRAGMA table_info(contact_point_profile_categories)").all()}
    if columns != expected:
        _corrupt()
    sql = connection.exec_driver_sql("SELECT sql FROM sqlite_master WHERE type='table' AND name='contact_point_profile_categories'").scalar_one_or_none() or ""
    normalized_sql = _canonical_expression(sql)
    if any(_canonical_expression(name) not in normalized_sql or _canonical_expression(check) not in normalized_sql for name, check in _CHECKS["contact_point_profile_categories"][:2]):
        _corrupt()
    _validate_indexes(connection, "contact_point_profile_categories")


def _validate_indexes(connection, table: str) -> None:
    rows = connection.exec_driver_sql(f"PRAGMA index_list({table})").all()
    unique_columns = set()
    indexed = {}
    for row in rows:
        name, unique, partial = str(row[1]), bool(row[2]), bool(row[4])
        columns = tuple(str(item[2]) for item in connection.exec_driver_sql(f"PRAGMA index_info({name})").all())
        indexed[name] = (unique, partial, columns)
        if unique and not partial:
            unique_columns.add(columns)
    if not _UNIQUE_COLUMNS[table] <= unique_columns:
        _corrupt()
    for name, (columns, predicate) in _PARTIAL_INDEXES.get(table, {}).items():
        actual = indexed.get(name)
        sql = connection.exec_driver_sql("SELECT sql FROM sqlite_master WHERE type='index' AND name=?", (name,)).scalar_one_or_none() or ""
        if actual != (True, True, columns) or _canonical_where(sql) != _canonical_expression(predicate):
            _corrupt()


def _canonical_where(sql: str) -> str:
    match = re.search(r"\bwhere\b(?P<expression>.+)$", sql, flags=re.IGNORECASE)
    return _canonical_expression(match.group("expression") if match else "")


def _canonical_expression(expression: str) -> str:
    return " ".join(re.findall(r"'(?:''|[^'])*'|<>|!=|<=|>=|[(),]|=|<|>|\b\w+\b", expression.lower()))


def _corrupt() -> None:
    raise RuntimeError("authority_corrupt: Point Profile table shape is incompatible.")
