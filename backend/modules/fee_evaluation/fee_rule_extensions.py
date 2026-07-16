"""Load reviewed source mappings and extension-only fee rules."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from backend.modules.fee_evaluation.fee_rule_models import (
    ALLOWED_CALCULATION_STRATEGIES,
    ALLOWED_UNIT_LABELS,
    SUPPORTED_EFFECTIVE_FROM_BASES,
    CalculationStrategy,
    FeeAmount,
    FeeRule,
    FeeRuleVersion,
)


EXPECTED_SOURCE_ROWS = frozenset(range(4, 48))
_SOURCE_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class FeeRuleExtensionError(ValueError):
    """Base error for an unreadable or invalid fee-rule extension set."""


class FeeRuleExtensionLoadError(FeeRuleExtensionError):
    """Raised when an extension file cannot be read or decoded."""


class FeeRuleExtensionValidationError(FeeRuleExtensionError):
    """Raised when an extension set violates its reviewed-data contract."""


@dataclass(frozen=True, slots=True)
class FeeSourceRuleExtension:
    """Reviewed runtime interpretation for one source workbook row."""

    source_row: int
    rule_id: str
    aliases: tuple[str, ...]
    base_fee_amount: Decimal | None
    unit_price_amount: Decimal | None
    unit_label: str
    calculation_strategy: CalculationStrategy
    review_required: bool
    review_reason: str | None


@dataclass(frozen=True, slots=True)
class FeeRuleExtensionSet:
    """Versioned source mappings plus ConnLab extension-only rules."""

    version: FeeRuleVersion
    source_rules: tuple[FeeSourceRuleExtension, ...]
    extension_rules: tuple[FeeRule, ...]


def load_fee_rule_extensions(path: Path) -> FeeRuleExtensionSet:
    """Load reviewed source mappings and extension-only fee rules."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FeeRuleExtensionLoadError(f"Unable to read fee rule extensions: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FeeRuleExtensionLoadError(f"Invalid JSON in fee rule extensions: {path}") from exc

    root = _mapping(payload, "extensions")
    version = _parse_version(root.get("version"))
    source_rules = _parse_source_rules(root.get("source_rules"))
    extension_rules = _parse_extension_rules(root.get("extension_rules"))
    _validate_coverage(source_rules)
    _validate_cross_section_identity(source_rules, extension_rules)
    return FeeRuleExtensionSet(
        version=version,
        source_rules=source_rules,
        extension_rules=extension_rules,
    )


def _parse_version(payload: Any) -> FeeRuleVersion:
    """Parse and validate runtime seed version metadata."""
    value = _mapping(payload, "version")
    version = FeeRuleVersion(
        version_id=_nonempty(value.get("version_id"), "version.version_id"),
        source_file_name=_nonempty(value.get("source_file_name"), "version.source_file_name"),
        source_sheet=_nonempty(value.get("source_sheet"), "version.source_sheet"),
        source_hash=_nonempty(value.get("source_hash"), "version.source_hash").lower(),
        effective_from_basis=_nonempty(
            value.get("effective_from_basis"),
            "version.effective_from_basis",
        ),
        created_at=_nonempty(value.get("created_at"), "version.created_at"),
    )
    if not _SOURCE_HASH_PATTERN.fullmatch(version.source_hash):
        raise FeeRuleExtensionValidationError("version.source_hash has invalid format.")
    if version.effective_from_basis not in SUPPORTED_EFFECTIVE_FROM_BASES:
        raise FeeRuleExtensionValidationError("version.effective_from_basis is unsupported.")
    try:
        datetime.fromisoformat(version.created_at)
    except ValueError as exc:
        raise FeeRuleExtensionValidationError("version.created_at must be ISO-8601 compatible.") from exc
    return version


def _parse_source_rules(payload: Any) -> tuple[FeeSourceRuleExtension, ...]:
    """Parse reviewed source-row mappings."""
    rules: list[FeeSourceRuleExtension] = []
    for index, entry in enumerate(_array(payload, "source_rules")):
        context = f"source_rules[{index}]"
        value = _mapping(entry, context)
        rule = FeeSourceRuleExtension(
            source_row=_integer(value.get("source_row"), f"{context}.source_row"),
            rule_id=_nonempty(value.get("rule_id"), f"{context}.rule_id"),
            aliases=_aliases(value.get("aliases"), f"{context}.aliases", required=False),
            base_fee_amount=_decimal(value.get("base_fee_amount"), f"{context}.base_fee_amount"),
            unit_price_amount=_decimal(
                value.get("unit_price_amount"),
                f"{context}.unit_price_amount",
            ),
            unit_label=_nonempty(value.get("unit_label"), f"{context}.unit_label"),
            calculation_strategy=_strategy(
                value.get("calculation_strategy"),
                f"{context}.calculation_strategy",
            ),
            review_required=_boolean(
                value.get("review_required"),
                f"{context}.review_required",
            ),
            review_reason=_optional_string(
                value.get("review_reason"),
                f"{context}.review_reason",
            ),
        )
        _validate_review(rule, context)
        _validate_unit(rule.unit_label, context)
        rules.append(rule)
    return tuple(rules)


def _parse_extension_rules(payload: Any) -> tuple[FeeRule, ...]:
    """Parse extension-only rules in the existing runtime model."""
    rules: list[FeeRule] = []
    for index, entry in enumerate(_array(payload, "extension_rules")):
        context = f"extension_rules[{index}]"
        value = _mapping(entry, context)
        rule = FeeRule(
            rule_id=_nonempty(value.get("rule_id"), f"{context}.rule_id"),
            display_name=_nonempty(value.get("display_name"), f"{context}.display_name"),
            aliases=_aliases(value.get("aliases"), f"{context}.aliases", required=True),
            base_fee=_amount(value.get("base_fee"), f"{context}.base_fee"),
            unit_price=_amount(value.get("unit_price"), f"{context}.unit_price"),
            unit_label=_nonempty(value.get("unit_label"), f"{context}.unit_label"),
            applicable_standard=_string(
                value.get("applicable_standard"),
                f"{context}.applicable_standard",
            ),
            range_condition=_string(value.get("range_condition"), f"{context}.range_condition"),
            calculation_strategy=_strategy(
                value.get("calculation_strategy"),
                f"{context}.calculation_strategy",
            ),
            review_required=_boolean(
                value.get("review_required"),
                f"{context}.review_required",
            ),
            review_reason=_optional_string(
                value.get("review_reason"),
                f"{context}.review_reason",
            ),
        )
        _validate_review(rule, context)
        _validate_unit(rule.unit_label, context)
        rules.append(rule)
    return tuple(rules)


def _validate_coverage(rules: tuple[FeeSourceRuleExtension, ...]) -> None:
    """Require exactly one source mapping for every effective source row."""
    row_numbers = [rule.source_row for rule in rules]
    duplicate = _first_duplicate(row_numbers)
    if duplicate is not None:
        raise FeeRuleExtensionValidationError(f"Duplicate source mapping: {duplicate}")
    actual = set(row_numbers)
    missing = sorted(EXPECTED_SOURCE_ROWS - actual)
    if missing:
        raise FeeRuleExtensionValidationError(f"Missing source mappings: {_joined(missing)}")
    unexpected = sorted(actual - EXPECTED_SOURCE_ROWS)
    if unexpected:
        raise FeeRuleExtensionValidationError(f"Unexpected source mappings: {_joined(unexpected)}")


def _validate_cross_section_identity(
    source_rules: tuple[FeeSourceRuleExtension, ...],
    extension_rules: tuple[FeeRule, ...],
) -> None:
    """Reject duplicate rule IDs and normalized aliases across both sections."""
    rule_ids: set[str] = set()
    aliases: dict[str, str] = {}
    for rule in (*source_rules, *extension_rules):
        if rule.rule_id in rule_ids:
            raise FeeRuleExtensionValidationError(f"Duplicate rule_id: {rule.rule_id}")
        rule_ids.add(rule.rule_id)
        for alias in rule.aliases:
            normalized = _normalize_alias(alias)
            prior = aliases.get(normalized)
            if prior is not None:
                raise FeeRuleExtensionValidationError(
                    f"Duplicate alias {alias!r} on {rule.rule_id}; already used by {prior}."
                )
            aliases[normalized] = rule.rule_id


def _validate_review(rule: FeeSourceRuleExtension | FeeRule, context: str) -> None:
    """Require review metadata for every reviewed or manual rule."""
    if rule.calculation_strategy == "manual_required" and not rule.review_required:
        raise FeeRuleExtensionValidationError(f"{context} manual rule must require review.")
    if rule.review_required and not (rule.review_reason or "").strip():
        raise FeeRuleExtensionValidationError(f"{context}.review_reason is required.")


def _validate_unit(unit_label: str, context: str) -> None:
    """Require one supported runtime unit label."""
    if unit_label not in ALLOWED_UNIT_LABELS:
        raise FeeRuleExtensionValidationError(f"{context}.unit_label is unsupported: {unit_label}")


def _amount(payload: Any, context: str) -> FeeAmount:
    """Parse one runtime amount while retaining reviewed display text."""
    value = _mapping(payload, context)
    return FeeAmount(
        amount=_decimal(value.get("amount"), f"{context}.amount"),
        text=_string(value.get("text"), f"{context}.text"),
    )


def _strategy(value: Any, context: str) -> CalculationStrategy:
    """Parse one supported calculation strategy."""
    strategy = _nonempty(value, context)
    if strategy not in ALLOWED_CALCULATION_STRATEGIES:
        raise FeeRuleExtensionValidationError(f"{context} is unsupported: {strategy}")
    return strategy  # type: ignore[return-value]


def _aliases(value: Any, context: str, *, required: bool) -> tuple[str, ...]:
    """Parse reviewed aliases and reject empty values."""
    aliases = tuple(_nonempty(item, f"{context}[]") for item in _array(value, context))
    if required and not aliases:
        raise FeeRuleExtensionValidationError(f"{context} must contain at least one alias.")
    return aliases


def _decimal(value: Any, context: str) -> Decimal | None:
    """Parse an optional decimal value."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise FeeRuleExtensionValidationError(f"{context} must be numeric or null.")
    try:
        return Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise FeeRuleExtensionValidationError(f"{context} must be numeric or null.") from exc


def _mapping(value: Any, context: str) -> dict[str, Any]:
    """Require a JSON object."""
    if not isinstance(value, dict):
        raise FeeRuleExtensionValidationError(f"{context} must be a JSON object.")
    return value


def _array(value: Any, context: str) -> list[Any]:
    """Require a JSON array."""
    if not isinstance(value, list):
        raise FeeRuleExtensionValidationError(f"{context} must be a JSON array.")
    return value


def _string(value: Any, context: str) -> str:
    """Require a JSON string without normalizing its contents."""
    if not isinstance(value, str):
        raise FeeRuleExtensionValidationError(f"{context} must be a string.")
    return value


def _nonempty(value: Any, context: str) -> str:
    """Require a non-empty JSON string."""
    text = _string(value, context)
    if not text.strip():
        raise FeeRuleExtensionValidationError(f"{context} is required.")
    return text


def _optional_string(value: Any, context: str) -> str | None:
    """Parse an optional normalized string."""
    if value is None:
        return None
    text = _string(value, context).strip()
    return text or None


def _integer(value: Any, context: str) -> int:
    """Require a JSON integer but reject booleans."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise FeeRuleExtensionValidationError(f"{context} must be an integer.")
    return value


def _boolean(value: Any, context: str) -> bool:
    """Require a JSON boolean."""
    if not isinstance(value, bool):
        raise FeeRuleExtensionValidationError(f"{context} must be a boolean.")
    return value


def _first_duplicate(values: list[int]) -> int | None:
    """Return the first duplicate integer in input order."""
    seen: set[int] = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def _joined(values: list[int]) -> str:
    """Format row numbers for stable validation messages."""
    return ", ".join(str(value) for value in values)


def _normalize_alias(value: str) -> str:
    """Normalize aliases consistently with the runtime seed validator."""
    return " ".join(re.split(r"[^a-z0-9\u4e00-\u9fff]+", value.lower().strip())).strip()
