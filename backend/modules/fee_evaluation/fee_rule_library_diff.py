"""Diff reviewed fee-rule libraries for maintenance review."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from backend.modules.fee_evaluation.fee_rule_models import FeeAmount, FeeRule, FeeRuleLibrary

FeeRuleDiffStatus = Literal["added", "removed", "changed", "unchanged"]


@dataclass(frozen=True, slots=True)
class FeeRuleFieldChange:
    """One changed field in a fee-rule diff entry."""

    field_name: str
    before: str
    after: str


@dataclass(frozen=True, slots=True)
class FeeRuleDiffEntry:
    """Diff classification for one fee rule id."""

    rule_id: str
    status: FeeRuleDiffStatus
    display_name: str
    field_changes: tuple[FeeRuleFieldChange, ...]


@dataclass(frozen=True, slots=True)
class FeeRuleLibraryDiff:
    """Deterministic diff between active and candidate fee-rule libraries."""

    active_version_id: str
    candidate_version_id: str
    added_count: int
    removed_count: int
    changed_count: int
    unchanged_count: int
    entries: tuple[FeeRuleDiffEntry, ...]


def diff_fee_rule_libraries(
    active: FeeRuleLibrary,
    candidate: FeeRuleLibrary,
) -> FeeRuleLibraryDiff:
    """Compare active and candidate libraries by rule id."""
    active_rules = {rule.rule_id: rule for rule in active.rules}
    candidate_rules = {rule.rule_id: rule for rule in candidate.rules}
    entries = tuple(
        _diff_rule(rule_id, active_rules.get(rule_id), candidate_rules.get(rule_id))
        for rule_id in sorted(active_rules.keys() | candidate_rules.keys())
    )
    return FeeRuleLibraryDiff(
        active_version_id=active.version.version_id,
        candidate_version_id=candidate.version.version_id,
        added_count=sum(1 for entry in entries if entry.status == "added"),
        removed_count=sum(1 for entry in entries if entry.status == "removed"),
        changed_count=sum(1 for entry in entries if entry.status == "changed"),
        unchanged_count=sum(1 for entry in entries if entry.status == "unchanged"),
        entries=entries,
    )


def _diff_rule(
    rule_id: str,
    active_rule: FeeRule | None,
    candidate_rule: FeeRule | None,
) -> FeeRuleDiffEntry:
    if active_rule is None and candidate_rule is not None:
        return FeeRuleDiffEntry(
            rule_id=rule_id,
            status="added",
            display_name=candidate_rule.display_name,
            field_changes=(),
        )
    if active_rule is not None and candidate_rule is None:
        return FeeRuleDiffEntry(
            rule_id=rule_id,
            status="removed",
            display_name=active_rule.display_name,
            field_changes=(),
        )
    if active_rule is None or candidate_rule is None:
        raise AssertionError("Unexpected empty rule pair during fee-rule diff.")
    changes = _field_changes(active_rule, candidate_rule)
    return FeeRuleDiffEntry(
        rule_id=rule_id,
        status="changed" if changes else "unchanged",
        display_name=candidate_rule.display_name,
        field_changes=tuple(changes),
    )


def _field_changes(active_rule: FeeRule, candidate_rule: FeeRule) -> list[FeeRuleFieldChange]:
    checks: tuple[tuple[str, str, str], ...] = (
        ("display_name", active_rule.display_name, candidate_rule.display_name),
        ("aliases", _tuple_text(active_rule.aliases), _tuple_text(candidate_rule.aliases)),
        ("base_fee", _amount_text(active_rule.base_fee), _amount_text(candidate_rule.base_fee)),
        ("unit_price", _amount_text(active_rule.unit_price), _amount_text(candidate_rule.unit_price)),
        ("unit_label", active_rule.unit_label, candidate_rule.unit_label),
        ("applicable_standard", active_rule.applicable_standard, candidate_rule.applicable_standard),
        ("range_condition", active_rule.range_condition, candidate_rule.range_condition),
        ("calculation_strategy", active_rule.calculation_strategy, candidate_rule.calculation_strategy),
        ("review_required", str(active_rule.review_required), str(candidate_rule.review_required)),
        ("review_reason", active_rule.review_reason or "", candidate_rule.review_reason or ""),
        ("source_kind", active_rule.source_kind, candidate_rule.source_kind),
        (
            "source_row",
            str(active_rule.source_row) if active_rule.source_row is not None else "",
            str(candidate_rule.source_row) if candidate_rule.source_row is not None else "",
        ),
    )
    return [
        FeeRuleFieldChange(field_name=field_name, before=before, after=after)
        for field_name, before, after in checks
        if before != after
    ]


def _tuple_text(values: tuple[str, ...]) -> str:
    return "\n".join(values)


def _amount_text(amount: FeeAmount) -> str:
    amount_value = str(amount.amount) if amount.amount is not None else ""
    return f"{amount_value}|{amount.text}"
