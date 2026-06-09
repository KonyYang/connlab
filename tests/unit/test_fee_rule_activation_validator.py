from __future__ import annotations

from dataclasses import replace

import pytest

from backend.modules.fee_evaluation import (
    FeeRuleActivationValidationError,
    FeeRuleLibrary,
    diff_fee_rule_libraries,
    validate_candidate_activation,
)
from tests.unit.test_fee_rule_library_diff import _rule, _version


def test_activation_validator_rejects_changed_content_with_reused_version_id() -> None:
    active = FeeRuleLibrary(version=_version("fee_rules_active"), rules=(_rule("rule_a"),))
    candidate = FeeRuleLibrary(
        version=_version("fee_rules_active"),
        rules=(_rule("rule_a"), _rule("rule_b")),
    )

    with pytest.raises(FeeRuleActivationValidationError, match="new version_id"):
        validate_candidate_activation(active, candidate, diff_fee_rule_libraries(active, candidate))


def test_activation_validator_rejects_metadata_only_change_with_reused_version_id() -> None:
    active = FeeRuleLibrary(version=_version("fee_rules_active"), rules=(_rule("rule_a"),))
    candidate = FeeRuleLibrary(
        version=replace(
            _version("fee_rules_active"),
            source_hash="sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        ),
        rules=(_rule("rule_a"),),
    )

    with pytest.raises(FeeRuleActivationValidationError, match="new version_id"):
        validate_candidate_activation(active, candidate, diff_fee_rule_libraries(active, candidate))


def test_activation_validator_allows_unchanged_same_version_as_noop() -> None:
    active = FeeRuleLibrary(version=_version("fee_rules_active"), rules=(_rule("rule_a"),))
    candidate = FeeRuleLibrary(version=_version("fee_rules_active"), rules=(_rule("rule_a"),))

    validate_candidate_activation(active, candidate, diff_fee_rule_libraries(active, candidate))


def test_activation_validator_allows_changed_candidate_with_new_version_id() -> None:
    active = FeeRuleLibrary(version=_version("fee_rules_active"), rules=(_rule("rule_a"),))
    candidate = FeeRuleLibrary(
        version=_version("fee_rules_v2026_06_10"),
        rules=(_rule("rule_a"), _rule("rule_b")),
    )

    validate_candidate_activation(active, candidate, diff_fee_rule_libraries(active, candidate))
