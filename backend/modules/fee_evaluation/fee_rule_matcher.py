"""Deterministic exact and conservative token matching for fee rules."""

from __future__ import annotations

import re

from backend.modules.fee_evaluation.fee_rule_models import (
    FeeRule,
    FeeRuleLibrary,
    FeeRuleMatchResult,
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+")
_MATING_UNMATING_FORCE_PATTERN = re.compile(
    r"^\s*mating\s*/\s*un\s*-?\s*mating\s+force\s*$",
    re.IGNORECASE,
)
_SINGLE_PIN_MATING_UNMATING_FORCE_PATTERN = re.compile(
    r"^\s*single\s+pin\s+mating\s*/\s*un\s*-?\s*mating\s+force\s*$",
    re.IGNORECASE,
)
_TOKEN_FALLBACK_BLOCKED_RULE_IDS = frozenset(
    {
        "fee_rule_mechanical_force",
        "fee_rule_automotive_mechanical_force",
    }
)


def normalize_fee_rule_text(value: str | None) -> str:
    """Normalize alias and Matrix test-item text for deterministic matching."""
    if value is None:
        return ""
    single_pin_key = _canonical_single_pin_mating_unmating_force(value)
    if single_pin_key is not None:
        return single_pin_key
    base_key = _canonical_mating_unmating_force(value)
    if base_key is not None:
        return base_key
    lowered = value.strip().lower()
    return " ".join(_TOKEN_PATTERN.findall(lowered))


def _canonical_mating_unmating_force(value: str) -> str | None:
    """Canonicalize only the complete base Mating/Un-mating Force label."""
    if _MATING_UNMATING_FORCE_PATTERN.fullmatch(value):
        return "mating un mating force"
    return None


def _canonical_single_pin_mating_unmating_force(value: str) -> str | None:
    """Canonicalize only the complete combined Single Pin force label."""
    if _SINGLE_PIN_MATING_UNMATING_FORCE_PATTERN.fullmatch(value):
        return "single pin mating force"
    return None


class FeeRuleMatcher:
    """Match Matrix-style test items to one reviewed fee rule or a stable no-match result."""

    def __init__(self, library: FeeRuleLibrary) -> None:
        self._library = library
        self._exact_alias_map = self._build_exact_alias_map(library.rules)

    def match_test_item(self, text: str | None) -> FeeRuleMatchResult:
        """Match one Matrix-style test item text against the reviewed fee-rule library."""
        normalized_text = normalize_fee_rule_text(text)
        if not normalized_text:
            return FeeRuleMatchResult(
                status="no_rule_match",
                rule=None,
                match_reason="Input text is empty after normalization.",
                review_required=True,
                review_reason="No fee rule match for empty test item text.",
            )

        exact_match = self._exact_alias_map.get(normalized_text)
        if exact_match is not None:
            return _matched_result(exact_match, "exact_alias_match")

        token_candidates = self._token_candidates(normalized_text)
        if not token_candidates:
            return FeeRuleMatchResult(
                status="no_rule_match",
                rule=None,
                match_reason="No deterministic fee rule alias matched the test item text.",
                review_required=True,
                review_reason="No fee rule match.",
            )
        if len(token_candidates) > 1:
            return FeeRuleMatchResult(
                status="no_rule_match",
                rule=None,
                match_reason=(
                    "Ambiguous token match across rules: "
                    + ", ".join(sorted(candidate.rule.rule_id for candidate in token_candidates))
                ),
                review_required=True,
                review_reason="Multiple fee rules matched the same test item text.",
            )
        return _matched_result(token_candidates[0].rule, f"token_alias_match:{token_candidates[0].alias}")

    def _token_candidates(self, normalized_text: str) -> list[_TokenCandidate]:
        text_tokens = set(normalized_text.split())
        candidates: list[_TokenCandidate] = []
        for rule in self._library.rules:
            if rule.rule_id in _TOKEN_FALLBACK_BLOCKED_RULE_IDS:
                continue
            best_alias: str | None = None
            best_score = -1
            for alias in rule.aliases:
                normalized_alias = normalize_fee_rule_text(alias)
                alias_tokens = normalized_alias.split()
                if len(alias_tokens) < 2:
                    continue
                if not set(alias_tokens).issubset(text_tokens):
                    continue
                if normalized_alias not in normalized_text and len(alias_tokens) < 3:
                    continue
                score = len(alias_tokens)
                if score > best_score:
                    best_alias = alias
                    best_score = score
            if best_alias is not None:
                candidates.append(_TokenCandidate(rule=rule, alias=best_alias, score=best_score))
        if not candidates:
            return []
        max_score = max(candidate.score for candidate in candidates)
        return [candidate for candidate in candidates if candidate.score == max_score]

    @staticmethod
    def _build_exact_alias_map(rules: tuple[FeeRule, ...]) -> dict[str, FeeRule]:
        alias_map: dict[str, FeeRule] = {}
        for rule in rules:
            for alias in rule.aliases:
                alias_map[normalize_fee_rule_text(alias)] = rule
        return alias_map


def match_fee_rule_text(library: FeeRuleLibrary, text: str | None) -> FeeRuleMatchResult:
    """Convenience function for one-off fee-rule matching."""
    return FeeRuleMatcher(library).match_test_item(text)


def _matched_result(rule: FeeRule, match_reason: str) -> FeeRuleMatchResult:
    return FeeRuleMatchResult(
        status="matched",
        rule=rule,
        match_reason=match_reason,
        review_required=rule.review_required,
        review_reason=rule.review_reason,
    )


class _TokenCandidate:
    def __init__(self, *, rule: FeeRule, alias: str, score: int) -> None:
        self.rule = rule
        self.alias = alias
        self.score = score
