"""Load and validate reviewed fee-rule seed JSON files."""

from __future__ import annotations

import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from importlib import resources
from pathlib import Path
from typing import Any

from backend.modules.fee_evaluation.fee_rule_models import (
    ALLOWED_CALCULATION_STRATEGIES,
    SUPPORTED_EFFECTIVE_FROM_BASES,
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleSeedValidationError,
    FeeRuleVersion,
)

_SOURCE_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_ACTIVE_SEED_PACKAGE = "backend.modules.fee_evaluation.seeds"
_ACTIVE_SEED_NAME = "fee_rules_v2026_06_03.json"


class FeeRuleSeedLoaderError(ValueError):
    """Raised when a seed file cannot be read or parsed."""


def load_active_fee_rule_library() -> FeeRuleLibrary:
    """Load the bundled active reviewed fee-rule seed."""
    seed_path = resources.files(_ACTIVE_SEED_PACKAGE).joinpath(_ACTIVE_SEED_NAME)
    with resources.as_file(seed_path) as resolved_path:
        return load_fee_rule_library(resolved_path)


def load_fee_rule_library(path: Path) -> FeeRuleLibrary:
    """Load and validate one fee-rule seed file from disk."""
    try:
        raw_payload = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FeeRuleSeedLoaderError(f"Unable to read fee rule seed file: {path}") from exc
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise FeeRuleSeedLoaderError(f"Invalid JSON in fee rule seed file: {path}") from exc

    library = _parse_library(payload)
    validate_fee_rule_library(library)
    return library


def validate_fee_rule_library(library: FeeRuleLibrary) -> None:
    """Validate metadata, rule identifiers, aliases, and strategy values."""
    version = library.version
    if not version.version_id.strip():
        raise FeeRuleSeedValidationError("version.version_id is required.")
    if not version.source_file_name.strip():
        raise FeeRuleSeedValidationError("version.source_file_name is required.")
    if version.source_sheet != "Unit Price Reference":
        raise FeeRuleSeedValidationError("version.source_sheet must be 'Unit Price Reference'.")
    if not _SOURCE_HASH_PATTERN.fullmatch(version.source_hash):
        raise FeeRuleSeedValidationError("version.source_hash must use format sha256:<64 lowercase hex>.")
    if version.effective_from_basis not in SUPPORTED_EFFECTIVE_FROM_BASES:
        raise FeeRuleSeedValidationError(
            "version.effective_from_basis must be one of: "
            + ", ".join(SUPPORTED_EFFECTIVE_FROM_BASES)
            + "."
        )
    _validate_created_at(version.created_at)
    if not library.rules:
        raise FeeRuleSeedValidationError("At least one fee rule is required.")

    seen_rule_ids: set[str] = set()
    seen_aliases: dict[str, str] = {}
    for rule in library.rules:
        if rule.rule_id in seen_rule_ids:
            raise FeeRuleSeedValidationError(f"Duplicate rule_id detected: {rule.rule_id}")
        seen_rule_ids.add(rule.rule_id)
        if not rule.display_name.strip():
            raise FeeRuleSeedValidationError(f"Rule {rule.rule_id} display_name is required.")
        if not rule.aliases:
            raise FeeRuleSeedValidationError(f"Rule {rule.rule_id} must define at least one alias.")
        if rule.calculation_strategy not in ALLOWED_CALCULATION_STRATEGIES:
            raise FeeRuleSeedValidationError(
                f"Rule {rule.rule_id} has unsupported calculation_strategy: "
                f"{rule.calculation_strategy}"
            )
        if rule.review_required and not (rule.review_reason or "").strip():
            raise FeeRuleSeedValidationError(
                f"Rule {rule.rule_id} must provide review_reason when review_required is true."
            )
        for alias in rule.aliases:
            normalized_alias = _normalize_alias_for_validation(alias)
            if not normalized_alias:
                raise FeeRuleSeedValidationError(f"Rule {rule.rule_id} contains an empty alias.")
            if normalized_alias in seen_aliases:
                prior_rule_id = seen_aliases[normalized_alias]
                raise FeeRuleSeedValidationError(
                    "Duplicate alias detected after normalization: "
                    f"{alias!r} on {rule.rule_id} conflicts with {prior_rule_id}."
                )
            seen_aliases[normalized_alias] = rule.rule_id


def _parse_library(payload: Any) -> FeeRuleLibrary:
    if not isinstance(payload, dict):
        raise FeeRuleSeedValidationError("Fee rule seed root must be a JSON object.")
    version_payload = _require_mapping(payload.get("version"), "version")
    rules_payload = payload.get("rules")
    if not isinstance(rules_payload, list):
        raise FeeRuleSeedValidationError("rules must be a JSON array.")
    version = FeeRuleVersion(
        version_id=_require_string(version_payload, "version_id", context="version"),
        source_file_name=_require_string(version_payload, "source_file_name", context="version"),
        source_sheet=_require_string(version_payload, "source_sheet", context="version"),
        source_hash=_require_string(version_payload, "source_hash", context="version").lower(),
        effective_from_basis=_require_string(
            version_payload,
            "effective_from_basis",
            context="version",
        ),
        created_at=_require_string(version_payload, "created_at", context="version"),
    )
    rules = tuple(_parse_rule(entry, index=index) for index, entry in enumerate(rules_payload))
    return FeeRuleLibrary(version=version, rules=rules)


def _parse_rule(payload: Any, *, index: int) -> FeeRule:
    context = f"rules[{index}]"
    rule_payload = _require_mapping(payload, context)
    aliases_payload = rule_payload.get("aliases")
    if not isinstance(aliases_payload, list):
        raise FeeRuleSeedValidationError(f"{context}.aliases must be a JSON array.")
    aliases = tuple(_require_string_value(alias, f"{context}.aliases[]") for alias in aliases_payload)
    review_required = _require_bool(rule_payload, "review_required", context=context)
    review_reason = _optional_string(rule_payload.get("review_reason"), f"{context}.review_reason")
    if not review_required and review_reason:
        review_reason = None
    return FeeRule(
        rule_id=_require_string(rule_payload, "rule_id", context=context),
        display_name=_require_string(rule_payload, "display_name", context=context),
        aliases=aliases,
        base_fee=_parse_amount(rule_payload.get("base_fee"), f"{context}.base_fee"),
        unit_price=_parse_amount(rule_payload.get("unit_price"), f"{context}.unit_price"),
        unit_label=_require_string(rule_payload, "unit_label", context=context),
        applicable_standard=_require_string(rule_payload, "applicable_standard", context=context),
        range_condition=_require_string(rule_payload, "range_condition", context=context),
        calculation_strategy=_require_string(rule_payload, "calculation_strategy", context=context),
        review_required=review_required,
        review_reason=review_reason,
    )


def _parse_amount(payload: Any, context: str) -> FeeAmount:
    amount_payload = _require_mapping(payload, context)
    raw_amount = amount_payload.get("amount")
    amount: Decimal | None
    if raw_amount is None:
        amount = None
    else:
        amount = _parse_decimal(raw_amount, f"{context}.amount")
    text = _require_string(amount_payload, "text", context=context)
    return FeeAmount(amount=amount, text=text)


def _require_mapping(payload: Any, context: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise FeeRuleSeedValidationError(f"{context} must be a JSON object.")
    return payload


def _require_string(mapping: dict[str, Any], key: str, *, context: str) -> str:
    return _require_string_value(mapping.get(key), f"{context}.{key}")


def _require_string_value(value: Any, context: str) -> str:
    if not isinstance(value, str):
        raise FeeRuleSeedValidationError(f"{context} must be a string.")
    return value.strip()


def _optional_string(value: Any, context: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FeeRuleSeedValidationError(f"{context} must be a string or null.")
    normalized = value.strip()
    return normalized or None


def _require_bool(mapping: dict[str, Any], key: str, *, context: str) -> bool:
    value = mapping.get(key)
    if not isinstance(value, bool):
        raise FeeRuleSeedValidationError(f"{context}.{key} must be a boolean.")
    return value


def _parse_decimal(value: Any, context: str) -> Decimal:
    if isinstance(value, (int, float)):
        value = str(value)
    if not isinstance(value, str):
        raise FeeRuleSeedValidationError(f"{context} must be a string, number, or null.")
    try:
        return Decimal(value.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise FeeRuleSeedValidationError(f"{context} must be a valid decimal value.") from exc


def _normalize_alias_for_validation(value: str) -> str:
    return " ".join(re.split(r"[^a-z0-9\u4e00-\u9fff]+", value.lower().strip())).strip()


def _validate_created_at(value: str) -> None:
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise FeeRuleSeedValidationError("version.created_at must be ISO-8601 compatible.") from exc
