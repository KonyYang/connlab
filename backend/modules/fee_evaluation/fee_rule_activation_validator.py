"""Activation safety checks for reviewed fee-rule candidates."""

from __future__ import annotations

from backend.modules.fee_evaluation.fee_rule_library_diff import FeeRuleLibraryDiff
from backend.modules.fee_evaluation.fee_rule_models import FeeRuleLibrary


class FeeRuleActivationValidationError(ValueError):
    """Raised when a candidate fee-rule library cannot be safely activated."""


def validate_candidate_activation(
    active: FeeRuleLibrary,
    candidate: FeeRuleLibrary,
    diff: FeeRuleLibraryDiff,
) -> None:
    """Validate that a changed candidate does not reuse the active version id."""
    same_version_id = active.version.version_id == candidate.version.version_id
    if not same_version_id:
        return
    if _has_rule_changes(diff) or _has_version_metadata_changes(active, candidate):
        raise FeeRuleActivationValidationError(
            "Changed fee rule candidates must use a new version_id before activation."
        )


def _has_rule_changes(diff: FeeRuleLibraryDiff) -> bool:
    return diff.added_count > 0 or diff.removed_count > 0 or diff.changed_count > 0


def _has_version_metadata_changes(active: FeeRuleLibrary, candidate: FeeRuleLibrary) -> bool:
    active_version = active.version
    candidate_version = candidate.version
    return (
        active_version.source_file_name != candidate_version.source_file_name
        or active_version.source_sheet != candidate_version.source_sheet
        or active_version.source_hash != candidate_version.source_hash
        or active_version.effective_from_basis != candidate_version.effective_from_basis
        or active_version.created_at != candidate_version.created_at
    )
