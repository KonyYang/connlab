"""Persist and reload Fee Evaluation pricing draft edits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    BuildMatrixBasicFeeTemplateCommand,
    ConfirmedMatrixFeeTemplateBasicFillService,
    MatrixBasicFillWorkbook,
    build_basic_fill_from_confirmed_snapshot,
)
from backend.application.fee_evaluation_pricing_draft_automatic_build import (
    build_current_pricing_defaults_if_supported,
    merge_existing_inactive_rows,
    validate_edited_values_against_captured_matrix,
)
from backend.application.fee_evaluation_pricing_draft_prior_defaults_attestation import (
    build_prior_defaults_attestation,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_from_json,
    edited_values_to_json,
    edited_values_to_payload,
)
from backend.application.fee_evaluation_pricing_draft_cas_policy import (
    save_cas_conflict_message,
)
from backend.application.fee_evaluation_pricing_draft_expectations import (
    context_conflict_message,
    discard_conflict_message,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeeEvaluationPricingDraftStatus,
    FeePricingDraftSourceContext,
    decode_pricing_draft_payload,
    encode_pricing_draft_v2,
    validation_token_for,
)
from backend.application.fee_evaluation_pricing_draft_v2_policy import (
    infer_operator_provenance,
)
from backend.application.fee_evaluation_pricing_draft_v2_authority_context import (
    basic_fill_context_values,
    build_legacy_source_context,
    current_automatic_values,
)
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.application.fee_rule_transition_safe_rebase import (
    load_rebase_candidate,
)

@dataclass(frozen=True, slots=True)
class SaveFeeEvaluationPricingDraftCommand:
    """Input for saving one project's current Fee Evaluation pricing draft."""

    project_id: str
    edited_values: FeeEvaluationEditedExportValues
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    expected_fee_rule_version_id: str | None = None
    expected_pricing_draft_edit_id: str | None = None
    expected_generation: int | None = None
    expected_payload_fingerprint: str | None = None
    expected_updated_at: str | None = None


@dataclass(frozen=True, slots=True)
class DiscardFeeEvaluationPricingDraftCommand:
    """Input for discarding one project's current Fee Evaluation pricing draft."""

    project_id: str
    expected_pricing_draft_edit_id: str | None = None
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    expected_fee_rule_version_id: str | None = None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftContext:
    """Current authority context used to bind a saved pricing draft."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    source_context: FeePricingDraftSourceContext | None = None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftSnapshot:
    """Persisted Fee Evaluation pricing draft edit payload."""

    draft_edit_id: str
    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    edited_values: FeeEvaluationEditedExportValues
    created_at: str
    updated_at: str
    generation: int | None = None
    payload_json: str | None = None
    payload_fingerprint: str | None = None
    source_context_fingerprint: str | None = None
    validation_token: str | None = None
    source_context: FeePricingDraftSourceContext | None = None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftCasExpectation:
    """Exact persisted state required before a V2 pricing-draft replacement."""

    draft_edit_id: str
    generation: int | None
    payload_fingerprint: str | None
    updated_at: str
    payload_json: str | None

    @classmethod
    def from_snapshot(
        cls, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> "FeeEvaluationPricingDraftCasExpectation":
        return cls(
            draft_edit_id=snapshot.draft_edit_id,
            generation=snapshot.generation,
            payload_fingerprint=snapshot.payload_fingerprint,
            updated_at=snapshot.updated_at,
            payload_json=snapshot.payload_json,
        )


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftLoadResult:
    """Load result for the current project's saved pricing draft."""

    status: FeeEvaluationPricingDraftStatus
    current_context: FeeEvaluationPricingDraftContext
    saved_snapshot: FeeEvaluationPricingDraftSnapshot | None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftDiscardResult:
    """Discard result for the current project's saved pricing draft."""

    discarded: bool
    current_context: FeeEvaluationPricingDraftContext


class FeeEvaluationPricingDraftConflictError(ValueError):
    """Raised when pricing draft optimistic context tokens do not match."""


class FeeEvaluationPricingDraftStore(Protocol):
    """Persistence operations required by the pricing draft service."""

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        """Create or replace the current draft for one authority/rule tuple."""

    def compare_and_swap(
        self,
        snapshot: FeeEvaluationPricingDraftSnapshot,
        expectation: FeeEvaluationPricingDraftCasExpectation | None,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Save only when the exact previous snapshot still exists."""

    def get_latest_by_project(
        self, project_id: str
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return the latest saved draft for one project, if any."""

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return the saved draft for an exact project/Matrix/rule context."""

    def delete_current(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> bool:
        """Delete the saved draft for an exact project/Matrix/rule context."""


class FeeEvaluationPricingDraftPersistenceService:
    """Save and reload Fee Evaluation pricing draft edits."""

    def __init__(
        self,
        *,
        basic_fill_service: ConfirmedMatrixFeeTemplateBasicFillService,
        draft_store: FeeEvaluationPricingDraftStore,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
        automatic_defaults_provider: object | None = None,
        point_profile_provider: object | None = None,
        measurement_plan_provider: object | None = None,
    ) -> None:
        self._basic_fill_service = basic_fill_service
        self._draft_store = draft_store
        self._lifecycle_write_guard = lifecycle_write_guard
        self._automatic_defaults_provider = automatic_defaults_provider
        self._point_profile_provider = point_profile_provider
        self._measurement_plan_provider = measurement_plan_provider

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        """Validate and persist one pricing draft for the current authority context."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.FEE_PRICING_DRAFT_SAVE,
        )
        automatic_build = build_current_pricing_defaults_if_supported(
            command.project_id, self._automatic_defaults_provider
        )
        basic_fill = (
            build_basic_fill_from_confirmed_snapshot(automatic_build.confirmed_matrix)
            if automatic_build is not None
            else self._build_basic_fill(command.project_id)
        )
        validate_edited_values_against_captured_matrix(command.edited_values, basic_fill)
        context = _context_from_basic_fill(basic_fill)
        context_conflict = context_conflict_message(command, context, operation="save")
        if context_conflict is not None:
            raise FeeEvaluationPricingDraftConflictError(context_conflict)
        now = datetime.now(timezone.utc).isoformat()
        existing = self._draft_store.get_by_context(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        draft_edit_id = existing.draft_edit_id if existing is not None else uuid4().hex
        created_at = existing.created_at if existing is not None else now
        edited_values = merge_existing_inactive_rows(
            incoming=command.edited_values,
            existing=existing.edited_values if existing is not None else None,
        )
        automatic_defaults = (
            automatic_build.automatic_values
            if automatic_build is not None
            else current_automatic_values(
                context.project_id,
                self._automatic_defaults_provider,
                edited_values,
            )
        )
        conflict_message = save_cas_conflict_message(command, existing)
        if conflict_message is not None:
            raise FeeEvaluationPricingDraftConflictError(conflict_message)
        generation = (existing.generation or 0) + 1 if existing is not None else 1
        source_context = (
            automatic_build.source_context
            if automatic_build is not None
            else self._legacy_source_context(context, edited_values)
        )
        attestation = (
            build_prior_defaults_attestation(
                generation=generation,
                source_context=source_context,
                automatic_values_payload=edited_values_to_payload(automatic_defaults),
                ordered_row_identities=automatic_build.ordered_row_identities,
                row_safety=automatic_build.row_safety,
            )
            if automatic_build is not None
            else None
        )
        payload_json = encode_pricing_draft_v2(
            generation=generation,
            source_context=source_context,
            edited_values_payload=edited_values_to_payload(edited_values),
            row_provenance=infer_operator_provenance(
                edited_values,
                automatic_defaults=automatic_defaults,
            ),
            summary_provenance=(),
            automatic_defaults_attestation=attestation,
        )
        decoded = decode_pricing_draft_payload(payload_json)
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=draft_edit_id,
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
            edited_values=edited_values,
            created_at=created_at,
            updated_at=now,
            generation=generation,
            payload_json=payload_json,
            payload_fingerprint=decoded.payload_fingerprint,
            source_context_fingerprint=decoded.source_context_fingerprint,
            validation_token=validation_token_for(
                draft_edit_id=draft_edit_id,
                generation=generation,
                source_context_fingerprint=decoded.source_context_fingerprint or "",
                payload_fingerprint=decoded.payload_fingerprint or "",
            ),
            source_context=source_context,
        )
        saved = self._save_snapshot(snapshot, existing)
        return FeeEvaluationPricingDraftLoadResult(
            status="current_v2",
            current_context=context,
            saved_snapshot=saved,
        )

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        """Load the saved pricing draft for the current authority context."""
        automatic_build = build_current_pricing_defaults_if_supported(
            project_id, self._automatic_defaults_provider
        )
        basic_fill = (
            build_basic_fill_from_confirmed_snapshot(automatic_build.confirmed_matrix)
            if automatic_build is not None
            else self._build_basic_fill(project_id)
        )
        context = _context_from_basic_fill(basic_fill)
        snapshot = self._draft_store.get_by_context(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        if snapshot is None:
            latest = self._draft_store.get_latest_by_project(project_id)
            if (
                latest is not None
                and latest.project_id == project_id
                and latest.generation is not None
                and latest.source_context is not None
            ):
                return self._load_rebase_candidate(
                    latest, context, project_id, automatic_build
                )
            return FeeEvaluationPricingDraftLoadResult(
                status="missing",
                current_context=context,
                saved_snapshot=None,
            )
        if snapshot.generation is None or snapshot.source_context is None:
            return FeeEvaluationPricingDraftLoadResult(
                status="legacy_unclassified",
                current_context=context,
                saved_snapshot=snapshot,
            )
        current_source_context = (
            automatic_build.source_context
            if automatic_build is not None
            else self._legacy_source_context(context, snapshot.edited_values)
        )
        if snapshot.source_context != current_source_context:
            # A review is required, but the operator must see the deterministic merge
            # rather than the obsolete values-only payload. This remains read-only.
            return self._load_rebase_candidate(
                snapshot, context, project_id, automatic_build
            )
        return FeeEvaluationPricingDraftLoadResult(
            status="current_v2",
            current_context=context,
            saved_snapshot=snapshot,
        )

    def _load_rebase_candidate(
        self,
        snapshot: FeeEvaluationPricingDraftSnapshot,
        context: FeeEvaluationPricingDraftContext,
        project_id: str,
        automatic_build: object | None,
    ) -> FeeEvaluationPricingDraftLoadResult:
        return load_rebase_candidate(
            snapshot=snapshot,
            context=context,
            project_id=project_id,
            automatic_defaults_provider=self._automatic_defaults_provider,
            current_source_context=(
                automatic_build.source_context
                if automatic_build is not None
                else self._legacy_source_context(context, snapshot.edited_values)
            ),
            current_automatic_build=automatic_build,
            result_type=FeeEvaluationPricingDraftLoadResult,
        )

    def discard(
        self, command: DiscardFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftDiscardResult:
        """Discard the saved pricing draft for the current authority context."""
        self._require_write_allowed(
            command.project_id,
            LifecycleWriteOperation.FEE_PRICING_DRAFT_DISCARD,
        )
        basic_fill = self._build_basic_fill(command.project_id)
        context = _context_from_basic_fill(basic_fill)
        snapshot = self._draft_store.get_by_context(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        if snapshot is None:
            return FeeEvaluationPricingDraftDiscardResult(
                discarded=False,
                current_context=context,
            )
        draft_conflict = discard_conflict_message(command, snapshot)
        context_conflict = context_conflict_message(command, context, operation="discard")
        if draft_conflict is not None:
            raise FeeEvaluationPricingDraftConflictError(draft_conflict)
        if context_conflict is not None:
            raise FeeEvaluationPricingDraftConflictError(context_conflict)
        discarded = self._draft_store.delete_current(
            project_id=context.project_id,
            confirmed_matrix_id=context.confirmed_matrix_id,
            confirmed_revision=context.confirmed_revision,
            fee_rule_version_id=context.fee_rule_version_id,
        )
        return FeeEvaluationPricingDraftDiscardResult(
            discarded=discarded,
            current_context=context,
        )

    def _require_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> None:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(project_id, operation)

    def _build_basic_fill(self, project_id: str) -> MatrixBasicFillWorkbook:
        """Build current backend Matrix basic-fill rows for validation/context."""
        return self._basic_fill_service.build(
            BuildMatrixBasicFeeTemplateCommand(project_id=project_id)
        )

    def _legacy_source_context(
        self,
        context: FeeEvaluationPricingDraftContext,
        fallback_values: FeeEvaluationEditedExportValues,
    ) -> FeePricingDraftSourceContext:
        return build_legacy_source_context(
            context=context,
            fallback_values=fallback_values,
            automatic_defaults_provider=self._automatic_defaults_provider,
            point_profile_provider=self._point_profile_provider,
            measurement_plan_provider=self._measurement_plan_provider,
        )

    def _save_snapshot(
        self,
        snapshot: FeeEvaluationPricingDraftSnapshot,
        existing: FeeEvaluationPricingDraftSnapshot | None,
    ) -> FeeEvaluationPricingDraftSnapshot:
        expectation = (
            FeeEvaluationPricingDraftCasExpectation.from_snapshot(existing)
            if existing is not None
            else None
        )
        compare_and_swap = getattr(self._draft_store, "compare_and_swap", None)
        if compare_and_swap is None:
            return self._draft_store.upsert_current(snapshot)
        saved = compare_and_swap(snapshot, expectation)
        if saved is None:
            raise FeeEvaluationPricingDraftConflictError(
                "Fee Evaluation pricing draft changed before save. Reload and review again."
            )
        return saved


def _context_from_basic_fill(
    basic_fill: MatrixBasicFillWorkbook,
) -> FeeEvaluationPricingDraftContext:
    return FeeEvaluationPricingDraftContext(**basic_fill_context_values(basic_fill))
