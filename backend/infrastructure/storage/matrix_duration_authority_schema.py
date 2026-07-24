"""All-or-nothing SQLite bootstrap for Matrix duration authority tables."""

from __future__ import annotations

import re

from sqlalchemy import CheckConstraint, ForeignKeyConstraint
from sqlalchemy.engine import Connection, Engine

from backend.infrastructure.storage.database import Base

MATRIX_DURATION_AUTHORITY_TABLES = (
    "source_matrix_duration_authorities",
    "project_matrix_draft_duration_authorities",
    "confirmed_matrix_duration_authorities",
)


class MatrixDurationAuthoritySchemaError(RuntimeError):
    """Raised when an existing duration-authority schema is incompatible."""


def bootstrap_matrix_duration_authority_schema(engine: Engine) -> None:
    """Create the full additive shape or fail closed on any partial shape."""
    tables = tuple(Base.metadata.tables[name] for name in MATRIX_DURATION_AUTHORITY_TABLES)
    if engine.dialect.name != "sqlite":
        Base.metadata.create_all(bind=engine, tables=list(tables))
        return
    with engine.connect() as connection:
        existing = _existing_tables(connection)
        present = existing.intersection(MATRIX_DURATION_AUTHORITY_TABLES)
        if present and present != set(MATRIX_DURATION_AUTHORITY_TABLES):
            raise MatrixDurationAuthoritySchemaError(
                "authority_corrupt: partial Matrix duration authority schema"
            )
        if present:
            _verify_shape(connection)
            return
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            for table in tables:
                table.create(connection, checkfirst=False)
            _verify_shape(connection)
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if isinstance(exc, MatrixDurationAuthoritySchemaError):
                raise
            raise MatrixDurationAuthoritySchemaError(
                "authority_corrupt: Matrix duration authority bootstrap failed"
            ) from exc


def _verify_shape(connection: Connection) -> None:
    for table_name in MATRIX_DURATION_AUTHORITY_TABLES:
        table = Base.metadata.tables[table_name]
        actual = {
            row[1]: (str(row[2]).upper(), bool(row[3]), bool(row[5]))
            for row in connection.exec_driver_sql(
                f'PRAGMA table_info("{table_name}")'
            ).all()
        }
        expected_names = {column.name for column in table.columns}
        if set(actual) != expected_names:
            raise MatrixDurationAuthoritySchemaError(
                f"authority_corrupt: incompatible {table_name} columns"
            )
        for column in table.columns:
            affinity, not_null, primary_key = actual[column.name]
            if bool(column.primary_key) != primary_key:
                raise MatrixDurationAuthoritySchemaError(
                    f"authority_corrupt: incompatible {table_name}.{column.name} primary key"
                )
            if not column.primary_key and (not column.nullable) != not_null:
                raise MatrixDurationAuthoritySchemaError(
                    f"authority_corrupt: incompatible {table_name}.{column.name} nullability"
                )
            if _affinity(str(column.type)) != _affinity(affinity):
                raise MatrixDurationAuthoritySchemaError(
                    f"authority_corrupt: incompatible {table_name}.{column.name} affinity"
                )
        expected_unique = next(
            constraint
            for constraint in table.constraints
            if constraint.__class__.__name__ == "UniqueConstraint"
        )
        expected_columns = [column.name for column in expected_unique.columns]
        unique_shapes = {
            tuple(
                row[2]
                for row in connection.exec_driver_sql(
                    f'PRAGMA index_info("{index[1]}")'
                ).all()
            )
            for index in connection.exec_driver_sql(
                f'PRAGMA index_list("{table_name}")'
            ).all()
            if bool(index[2])
        }
        if tuple(expected_columns) not in unique_shapes:
            raise MatrixDurationAuthoritySchemaError(
                f"authority_corrupt: missing {table_name} unique identity"
            )
        _verify_foreign_keys(connection, table_name, table)
        _verify_named_checks(connection, table_name, table)


def _verify_foreign_keys(connection: Connection, table_name: str, table) -> None:
    actual = {
        (
            row[3],
            row[2],
            row[4],
            row[5].upper(),
            row[6].upper(),
            row[7].upper(),
        )
        for row in connection.exec_driver_sql(
            f'PRAGMA foreign_key_list("{table_name}")'
        ).all()
    }
    expected: set[tuple[str, str, str, str, str, str]] = set()
    for constraint in table.constraints:
        if not isinstance(constraint, ForeignKeyConstraint):
            continue
        for local, remote in zip(constraint.columns, constraint.elements):
            expected.add(
                (
                    local.name,
                    remote.column.table.name,
                    remote.column.name,
                    (constraint.onupdate or "NO ACTION").upper(),
                    (constraint.ondelete or "NO ACTION").upper(),
                    (constraint.match or "NONE").upper(),
                )
            )
    if actual != expected:
        raise MatrixDurationAuthoritySchemaError(
            f"authority_corrupt: incompatible {table_name} foreign keys"
        )


def _verify_named_checks(connection: Connection, table_name: str, table) -> None:
    row = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,),
    ).one_or_none()
    table_sql = row[0] if row and isinstance(row[0], str) else ""
    actual = _named_check_expressions(table_sql)
    expected = {
        constraint.name: _normalize_sql_expression(str(constraint.sqltext))
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint) and constraint.name
    }
    if actual != expected:
        raise MatrixDurationAuthoritySchemaError(
            f"authority_corrupt: incompatible {table_name} named checks"
        )


def _named_check_expressions(sql: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(
        r"\bCONSTRAINT\s+[\"`\[]?(?P<name>[\w-]+)[\"`\]]?\s+CHECK\s*\(",
        re.IGNORECASE,
    )
    for match in pattern.finditer(sql):
        start = match.end()
        depth = 1
        index = start
        while index < len(sql) and depth:
            if sql[index] == "(":
                depth += 1
            elif sql[index] == ")":
                depth -= 1
            index += 1
        if depth:
            return {}
        result[match.group("name")] = _normalize_sql_expression(
            sql[start : index - 1]
        )
    return result


def _normalize_sql_expression(value: str) -> str:
    tokens = re.findall(
        r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`[^`]*`|\[[^\]]*\]|"
        r"<=|>=|<>|!=|==|[(),=<>+\-*/]|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?",
        value,
    )
    return "".join(
        token[1:-1].lower()
        if token[:1] in {'"', "`", "["} and token[-1:] in {'"', "`", "]"}
        else token.lower()
        for token in tokens
    )


def _existing_tables(connection: Connection) -> set[str]:
    return {
        row[0]
        for row in connection.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).all()
    }


def _affinity(type_name: str) -> str:
    value = type_name.upper()
    if "INT" in value:
        return "INTEGER"
    if any(token in value for token in ("CHAR", "CLOB", "TEXT")):
        return "TEXT"
    if any(token in value for token in ("REAL", "FLOA", "DOUB")):
        return "REAL"
    if not value or "BLOB" in value:
        return "BLOB"
    return "NUMERIC"
