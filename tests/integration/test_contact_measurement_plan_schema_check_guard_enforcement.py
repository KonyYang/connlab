"""Disposable TASK_361G guard-event coverage for all authority CHECK predicates."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError

from backend.infrastructure.storage.database import create_database_engine, init_db
from tests.integration.test_contact_measurement_plan_schema_check_compatibility_startup import (
    _fresh_authority_database,
    _insert_impact,
    _insert_target,
    _remove_authority_checks,
)


@pytest.mark.parametrize(
    ("label", "invalid_values", "column", "invalid_update_value", "expected_value"),
    (
        (
            "group_anchor_xor",
            {"manual_group_anchor_id": "manual-group"},
            "manual_group_anchor_id",
            "manual-group",
            None,
        ),
        (
            "row_anchor_xor",
            {"manual_row_anchor_id": "manual-row"},
            "manual_row_anchor_id",
            "manual-row",
            None,
        ),
        (
            "stable_target_key_prefix",
            {"stable_target_key": "not-a-target-key"},
            "stable_target_key",
            "not-a-target-key",
            "cmp-target:v1|target-valid",
        ),
    ),
)
def test_target_guard_rejects_each_predicate_on_insert_and_update(
    tmp_path: Path,
    label: str,
    invalid_values: dict[str, str],
    column: str,
    invalid_update_value: str,
    expected_value: str | None,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        with pytest.raises(IntegrityError, match="target CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                values = dict(invalid_values)
                stable_target_key = values.pop("stable_target_key", "cmp-target:v1|target-invalid")
                _insert_target(connection, f"target-invalid-{label}", stable_target_key, **values)
        with recovered_engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT COUNT(*) FROM measurement_plan_target_snapshots "
                "WHERE measurement_plan_target_snapshot_id=?",
                (f"target-invalid-{label}",),
            ).scalar_one() == 0

        valid_id = f"target-valid-{label}"
        with recovered_engine.begin() as connection:
            _insert_target(connection, valid_id, "cmp-target:v1|target-valid")
        with pytest.raises(IntegrityError, match="target CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                connection.exec_driver_sql(
                    f"UPDATE measurement_plan_target_snapshots SET {column}=? "
                    "WHERE measurement_plan_target_snapshot_id=?",
                    (invalid_update_value, valid_id),
                )
        with recovered_engine.connect() as connection:
            assert connection.exec_driver_sql(
                f"SELECT {column} FROM measurement_plan_target_snapshots "
                "WHERE measurement_plan_target_snapshot_id=?",
                (valid_id,),
            ).scalar_one() == expected_value
    finally:
        recovered_engine.dispose()


@pytest.mark.parametrize(
    ("label", "invalid_subject", "invalid_identity", "column", "invalid_update_value", "expected_value"),
    (
        (
            "impact_subject_prefix",
            "not-an-impact-subject",
            "cmp-impact:v1|impact-invalid",
            "impact_subject_key",
            "not-an-impact-subject",
            "cmp-target:v1|target-valid",
        ),
        (
            "impact_identity_prefix",
            "cmp-target:v1|target-invalid",
            "not-an-impact-identity",
            "impact_identity_key",
            "not-an-impact-identity",
            "cmp-impact:v1|impact-valid",
        ),
    ),
)
def test_impact_guard_rejects_each_predicate_on_insert_and_update(
    tmp_path: Path,
    label: str,
    invalid_subject: str,
    invalid_identity: str,
    column: str,
    invalid_update_value: str,
    expected_value: str,
) -> None:
    engine, settings = _fresh_authority_database(tmp_path)
    try:
        with engine.begin() as connection:
            _remove_authority_checks(connection)
    finally:
        engine.dispose()

    recovered_engine = create_database_engine(settings)
    try:
        init_db(recovered_engine)
        with pytest.raises(IntegrityError, match="impact CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                _insert_impact(
                    connection,
                    f"impact-invalid-{label}",
                    invalid_identity,
                    impact_subject_key=invalid_subject,
                )
        with recovered_engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT COUNT(*) FROM measurement_plan_impacts "
                "WHERE measurement_plan_impact_id=?",
                (f"impact-invalid-{label}",),
            ).scalar_one() == 0

        valid_id = f"impact-valid-{label}"
        with recovered_engine.begin() as connection:
            _insert_impact(
                connection,
                valid_id,
                "cmp-impact:v1|impact-valid",
                impact_subject_key="cmp-target:v1|target-valid",
            )
        with pytest.raises(IntegrityError, match="impact CHECK compatibility guard"):
            with recovered_engine.begin() as connection:
                connection.exec_driver_sql(
                    f"UPDATE measurement_plan_impacts SET {column}=? "
                    "WHERE measurement_plan_impact_id=?",
                    (invalid_update_value, valid_id),
                )
        with recovered_engine.connect() as connection:
            assert connection.exec_driver_sql(
                f"SELECT {column} FROM measurement_plan_impacts "
                "WHERE measurement_plan_impact_id=?",
                (valid_id,),
            ).scalar_one() == expected_value
    finally:
        recovered_engine.dispose()
