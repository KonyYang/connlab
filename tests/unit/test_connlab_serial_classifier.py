from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_serial_complex import SerialContractError, classify_request


ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = {
    "api_contract": False,
    "database": False,
    "schema_or_migration": False,
    "persistence": False,
    "authority": False,
    "public_drive_workflow": False,
    "business_rule_semantics": False,
    "destructive_action": False,
    "external_mutation": False,
    "push_or_release": False,
}


def complete_request() -> dict:
    return {
        "schema": "connlab.serial-task-request",
        "version": 1,
        "task_id": "TASK_CLASSIFY",
        "summary": "Fix one bounded defect.",
        "root_cause_clear": True,
        "expected_result_clear": True,
        "may_touch": ["docs/task_board.md", "scripts/fix.py"],
        "targeted_validation": ["py -m pytest tests/unit/test_fix.py -q"],
        "requires_independent_review": False,
        "forbidden_categories": copy.deepcopy(FORBIDDEN),
    }


def test_complete_bounded_request_classifies_simple() -> None:
    result = classify_request(complete_request())

    assert result == {"classification": "simple", "reason_codes": ["SIMPLE_PREDICATES_PASS"]}


@pytest.mark.parametrize("category", list(FORBIDDEN))
def test_each_forbidden_category_classifies_complex(category: str) -> None:
    payload = complete_request()
    payload["forbidden_categories"][category] = True

    result = classify_request(payload)

    assert result["classification"] == "complex"
    assert result["reason_codes"] == [f"FORBIDDEN_{category.upper()}"]


def test_missing_decision_fact_classifies_needs_discovery() -> None:
    payload = complete_request()
    del payload["root_cause_clear"]

    result = classify_request(payload)

    assert result == {
        "classification": "needs_discovery",
        "reason_codes": ["MISSING_ROOT_CAUSE_CLEAR"],
    }


def test_more_than_three_total_paths_classifies_complex() -> None:
    payload = complete_request()
    payload["may_touch"] = [
        "docs/task_board.md",
        "scripts/a.py",
        "scripts/b.py",
        "tests/unit/test_b.py",
    ]

    result = classify_request(payload)

    assert result == {"classification": "complex", "reason_codes": ["PATH_COUNT_EXCEEDS_SIMPLE"]}


def test_unknown_field_is_rejected_instead_of_ignored() -> None:
    payload = complete_request()
    payload["caller_claim"] = "simple"

    with pytest.raises(SerialContractError) as caught:
        classify_request(payload)

    assert caught.value.code == "BLOCKED_CLASSIFICATION_INVALID"


def test_public_writer_exposes_read_only_classification_without_board_change() -> None:
    before = (ROOT / "docs/task_board.md").read_bytes()
    completed = subprocess.run(
        [
            "py", str(ROOT / "scripts/connlab_personal_task.py"), "classify",
            "--repo-root", str(ROOT), "--request-json", json.dumps(complete_request()), "--json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["schema"] == "connlab.serial-task-result"
    assert result["code"] == "ALLOW_CLASSIFY_SIMPLE"
    assert result["classification"] == "simple"
    assert (ROOT / "docs/task_board.md").read_bytes() == before
