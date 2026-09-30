"""Promote pending Matrix-to-Fee rebase output after Matrix Confirm."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Literal, Protocol
from uuid import uuid4

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftService,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    build_basic_fill_from_confirmed_snapshot,
)
from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    ContactMeasurementPlanConfirmedConsumerAdapter,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    ContactPointProfileConfirmedConsumerAdapter,
)
from backend.application.confirmed_fee_review_markers import AUTO_REBASE_FEE_CONFIRMATION_NOTE
from backend.application.confirmed_fee_pricing_snapshot import (
    encode_confirmed_fee_pricing_snapshot,
    edited_values_payload_from_confirmed_fee_snapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedInactiveRow,
    FeeEvaluationEditedInactiveRowKey,
    edited_row_lookup,
    validate_supported_manual_rows,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_from_payload,
    edited_values_to_json,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeDraftRebaseService,
    MatrixFeeInactiveRemovedRow,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSummary,
)
from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseSnapshot,
    _filter_hard_deleted_inactive_rows,
    _source_rows_from_basic_fill,
    _structural_rebase_keys_from_matrix_draft,
    _target_groups_from_matrix_draft,
    _target_rows_from_matrix_draft,
    pending_rebase_payload_from_json,
)
from backend.application.matrix_fee_rebase_promotion_values import (
    active_only_edited_values,
    blank_summary,
    confirmed_fee_matches_snapshot,
    edited_values_from_fee_draft,
    index_new_basic_fill_by_draft_identity,
    remap_manual_row,
    remap_row,
    summary_from_edited_values,
)
from backend.application.matrix_fee_rebase_pricing_draft_bridge import FeePricingDraftPersistencePort, persist_current_v2_pricing_draft
from backend.domain import ConfirmedMatrixSnapshot, ProjectMatrixDraftSnapshot
from backend.domain.confirmed_fee import ConfirmedFeeVersion

MatrixFeeRebasePromotionStatus = Literal[
    "not_required",
    "promoted",
    "fallback_promoted",
    "default_promoted",
    "skipped",
    "failed",
]


@dataclass(frozen=True, slots=True)
class PromoteMatrixFeeRebaseCommand:
    """Input for promoting a Matrix autosave rebase after Matrix Confirm."""

    project_id: str
    saved_matrix_draft: ProjectMatrixDraftSnapshot
    saved_matrix_draft_payload_signature: str
    previous_confirmed_matrix: ConfirmedMatrixSnapshot
    new_confirmed_matrix: ConfirmedMatrixSnapshot
    fee_rule_version_id: str


@dataclass(frozen=True, slots=True)
class MatrixFeeRebasePromotionResult:
    """Non-fatal Matrix Confirm promotion result."""

    status: MatrixFeeRebasePromotionStatus
    summary: MatrixFeeRebaseSummary | None = None
    error: str | None = None


class MatrixFeePendingRebaseReadStore(Protocol):
    """Pending rebase read/delete operations needed by promotion."""

    def get_by_context(
        self,
        *,
        project_matrix_draft_id: str,
        fee_rule_version_id: str,
    ) -> MatrixFeePendingRebaseSnapshot | None:
        """Return pending rebase for one Matrix draft/rule context."""

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int:
        """Delete pending rebase rows for one Matrix draft."""


class FeePricingDraftPromotionStore(Protocol):
    """Pricing draft operations needed by promotion."""

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return pricing draft for one exact context."""

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        """Create or replace pricing draft for one exact context."""


class ConfirmedFeePromotionStore(Protocol):
    """Confirmed Fee authority operations needed by Matrix Confirm promotion."""

    def create(self, version: ConfirmedFeeVersion) -> ConfirmedFeeVersion:
        """Persist one Confirmed Fee authority version."""

    def get_latest_by_project(self, project_id: str) -> ConfirmedFeeVersion | None:
        """Return latest Confirmed Fee version for one project."""

    def list_by_project(self, project_id: str) -> tuple[ConfirmedFeeVersion, ...]:
        """Return Confirmed Fee versions for one project ordered ascending."""


class ConfirmedMatrixHistoryStore(Protocol):
    def get(self, confirmed_matrix_id: str) -> ConfirmedMatrixSnapshot | None:
        """Read the Matrix snapshot used by an earlier Fee confirmation."""


class MatrixFeeRebasePromotionService:
    """Promote pending or fallback Matrix-to-Fee rebase output."""

    def __init__(
        self,
        *,
        pending_store: MatrixFeePendingRebaseReadStore,
        pricing_draft_store: FeePricingDraftPromotionStore,
        confirmed_fee_store: ConfirmedFeePromotionStore | None = None,
        confirmed_matrix_store: ConfirmedMatrixHistoryStore | None = None,
        rebase_service: MatrixFeeDraftRebaseService | None = None,
        contact_measurement_adapter: ContactMeasurementPlanConfirmedConsumerAdapter | None = None,
        contact_point_profile_adapter: ContactPointProfileConfirmedConsumerAdapter | None = None,
        pricing_draft_persistence_service: FeePricingDraftPersistencePort | None = None,
    ) -> None:
        self._pending_store = pending_store
        self._pricing_draft_store = pricing_draft_store
        self._confirmed_fee_store = confirmed_fee_store
        self._confirmed_matrix_store = confirmed_matrix_store
        self._rebase = rebase_service or MatrixFeeDraftRebaseService()
        self._contact_measurement_adapter = contact_measurement_adapter
        self._contact_point_profile_adapter = contact_point_profile_adapter
        self._pricing_draft_persistence_service = pricing_draft_persistence_service

    def initialize_after_first_matrix_confirm(
        self,
        *,
        project_id: str,
        new_confirmed_matrix: ConfirmedMatrixSnapshot,
        fee_rule_version_id: str,
    ) -> MatrixFeeRebasePromotionResult:
        """Keep the existing first-Matrix Fee initialization behavior."""
        try:
            snapshot = self._save_default_draft(
                project_id=project_id,
                new_confirmed_matrix=new_confirmed_matrix,
                fee_rule_version_id=fee_rule_version_id,
            )
            self._confirm_default_fee(project_id=project_id, snapshot=snapshot)
            return MatrixFeeRebasePromotionResult(status="default_promoted")
        except Exception as exc:  # noqa: BLE001 - non-fatal Matrix Confirm boundary.
            return MatrixFeeRebasePromotionResult(
                status="failed",
                error=f"Fee default promotion failed: {exc}",
            )

    def promote_after_matrix_confirm(
        self,
        command: PromoteMatrixFeeRebaseCommand,
    ) -> MatrixFeeRebasePromotionResult:
        """Best-effort promotion that never fails Matrix Confirm."""
        try:
            if self._confirmed_fee_store is not None:
                confirmed_source = self._load_confirmed_source(command)
                if confirmed_source is None:
                    self._save_default_draft(
                        project_id=command.project_id,
                        new_confirmed_matrix=command.new_confirmed_matrix,
                        fee_rule_version_id=command.fee_rule_version_id,
                    )
                    return MatrixFeeRebasePromotionResult(status="default_promoted")
                source_pricing, source_matrix = confirmed_source
                result = self._fallback_rebase(command, source_pricing, source_matrix)
                edited_values = remap_rebase_result_to_confirmed_matrix(
                    rebase_result=result,
                    previous_pricing_draft=source_pricing,
                    new_confirmed_matrix=command.new_confirmed_matrix,
                )
                self._save_promoted_draft(command, edited_values)
                self._pending_store.delete_by_matrix_draft(
                    command.saved_matrix_draft.record.project_matrix_draft_id
                )
                return MatrixFeeRebasePromotionResult(
                    status="fallback_promoted", summary=result.summary,
                )
            previous_pricing = self._load_previous_pricing(command)
            pending = self._pending_store.get_by_context(
                project_matrix_draft_id=(
                    command.saved_matrix_draft.record.project_matrix_draft_id
                ),
                fee_rule_version_id=command.fee_rule_version_id,
            )
            if _pending_matches_command(pending, command):
                if previous_pricing is None:
                    snapshot = self._save_default_draft(
                        project_id=command.project_id,
                        new_confirmed_matrix=command.new_confirmed_matrix,
                        fee_rule_version_id=command.fee_rule_version_id,
                    )
                    self._confirm_default_fee(
                        project_id=command.project_id,
                        snapshot=snapshot,
                    )
                    return MatrixFeeRebasePromotionResult(status="default_promoted")
                result = pending_rebase_payload_from_json(pending.payload_json)
                edited_values = remap_rebase_result_to_confirmed_matrix(
                    rebase_result=result,
                    previous_pricing_draft=previous_pricing,
                    new_confirmed_matrix=command.new_confirmed_matrix,
                )
                self._save_promoted_draft(command, edited_values)
                self._pending_store.delete_by_matrix_draft(
                    command.saved_matrix_draft.record.project_matrix_draft_id
                )
                new_version = command.new_confirmed_matrix.version
                snapshot = self._pricing_draft_store.get_by_context(
                    project_id=command.project_id,
                    confirmed_matrix_id=new_version.confirmed_matrix_id,
                    confirmed_revision=new_version.confirmed_revision,
                    fee_rule_version_id=command.fee_rule_version_id,
                )
                if snapshot is not None:
                    self._confirm_default_fee(
                        project_id=command.project_id,
                        snapshot=snapshot,
                    )
                return MatrixFeeRebasePromotionResult(
                    status="promoted",
                    summary=result.summary,
                )
            if previous_pricing is None:
                snapshot = self._save_default_draft(
                    project_id=command.project_id,
                    new_confirmed_matrix=command.new_confirmed_matrix,
                    fee_rule_version_id=command.fee_rule_version_id,
                )
                self._confirm_default_fee(project_id=command.project_id, snapshot=snapshot)
                return MatrixFeeRebasePromotionResult(status="default_promoted")
            result = self._fallback_rebase(command, previous_pricing)
            edited_values = remap_rebase_result_to_confirmed_matrix(
                rebase_result=result,
                previous_pricing_draft=previous_pricing,
                new_confirmed_matrix=command.new_confirmed_matrix,
            )
            snapshot = self._save_promoted_draft(command, edited_values)
            self._confirm_default_fee(project_id=command.project_id, snapshot=snapshot)
            return MatrixFeeRebasePromotionResult(
                status="fallback_promoted",
                summary=result.summary,
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal Matrix Confirm boundary.
            return MatrixFeeRebasePromotionResult(
                status="failed",
                error=f"Fee rebase promotion failed: {exc}",
            )

    def _load_confirmed_source(
        self,
        command: PromoteMatrixFeeRebaseCommand,
    ) -> tuple[FeeEvaluationPricingDraftSnapshot, ConfirmedMatrixSnapshot] | None:
        assert self._confirmed_fee_store is not None
        reviewed = next(
            (version for version in reversed(self._confirmed_fee_store.list_by_project(command.project_id))
             if version.confirmed_by != "ConnLab Auto"),
            None,
        )
        if reviewed is None or reviewed.fee_rule_version_id != command.fee_rule_version_id:
            return None
        if reviewed.confirmed_matrix_id == command.previous_confirmed_matrix.version.confirmed_matrix_id:
            source_matrix = command.previous_confirmed_matrix
        elif self._confirmed_matrix_store is not None:
            source_matrix = self._confirmed_matrix_store.get(reviewed.confirmed_matrix_id)
        else:
            raise ValueError("Confirmed Fee source Matrix history is unavailable.")
        if source_matrix is None or source_matrix.version.project_id != command.project_id:
            raise ValueError("Confirmed Fee source Matrix history is unavailable.")
        payload = edited_values_payload_from_confirmed_fee_snapshot(reviewed.pricing_snapshot_json)
        if payload is None:
            raise ValueError("Confirmed Fee source values cannot be read safely.")
        source_pricing = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=reviewed.pricing_draft_edit_id,
            project_id=reviewed.project_id,
            confirmed_matrix_id=reviewed.confirmed_matrix_id,
            confirmed_revision=reviewed.confirmed_revision,
            fee_rule_version_id=reviewed.fee_rule_version_id,
            edited_values=edited_values_from_payload(dict(payload)),
            created_at=reviewed.confirmed_at,
            updated_at=reviewed.confirmed_at,
        )
        return source_pricing, source_matrix

    def _load_previous_pricing(
        self,
        command: PromoteMatrixFeeRebaseCommand,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        previous = command.previous_confirmed_matrix.version
        return self._pricing_draft_store.get_by_context(
            project_id=command.project_id,
            confirmed_matrix_id=previous.confirmed_matrix_id,
            confirmed_revision=previous.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
        )

    def _fallback_rebase(
        self,
        command: PromoteMatrixFeeRebaseCommand,
        previous_pricing: FeeEvaluationPricingDraftSnapshot,
        source_matrix: ConfirmedMatrixSnapshot | None = None,
    ) -> MatrixFeeRebaseResult:
        previous_basic_fill = build_basic_fill_from_confirmed_snapshot(
            source_matrix or command.previous_confirmed_matrix
        )
        structural_keys = _structural_rebase_keys_from_matrix_draft(
            command.saved_matrix_draft
        )
        source_defaults = self._automatic_values(
            command.project_id, source_matrix or command.previous_confirmed_matrix
        )
        target_defaults = self._automatic_values(
            command.project_id, command.new_confirmed_matrix
        )
        result = self._rebase.rebase(
            source_rows=_source_rows_from_basic_fill(
                previous_basic_fill.groups,
                source_values=previous_pricing.edited_values,
                structural_keys=structural_keys,
                source_defaults=source_defaults,
            ),
            target_rows=self._target_rows_with_defaults(command, target_defaults),
            source_manual_rows=previous_pricing.edited_values.manual_rows,
            target_groups=_target_groups_from_matrix_draft(command.saved_matrix_draft),
            source_manual_defaults=source_defaults.manual_rows,
            target_manual_defaults=target_defaults.manual_rows,
        )
        return _filter_hard_deleted_inactive_rows(
            result,
            structural_keys=structural_keys,
        )

    def _automatic_values(
        self, project_id: str, matrix: ConfirmedMatrixSnapshot,
    ) -> FeeEvaluationEditedExportValues:
        draft = ConfirmedMatrixFeeDraftService(
            confirmed_store=_SingleConfirmedMatrixStore(matrix),
            contact_measurement_adapter=self._contact_measurement_adapter,
            contact_point_profile_adapter=self._contact_point_profile_adapter,
        ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id=project_id))
        return edited_values_from_fee_draft(draft)

    def _target_rows_with_defaults(
        self, command: PromoteMatrixFeeRebaseCommand,
        current_defaults: FeeEvaluationEditedExportValues,
    ):
        matrix = command.new_confirmed_matrix
        group_ids = {group.confirmed_group_id: group.draft_group_id for group in matrix.groups}
        row_ids = {row.confirmed_row_id: row.draft_row_id for row in matrix.rows}
        by_draft_identity = {
            (group_ids[row.confirmed_group_id], row_ids[row.confirmed_row_id],
             row.step_token, row.step_index): row
            for row in current_defaults.rows
        }
        targets = []
        for target in _target_rows_from_matrix_draft(command.saved_matrix_draft):
            current = by_draft_identity.get(
                (target.lineage.confirmed_group_id, target.lineage.confirmed_row_id,
                 target.lineage.step_token, target.lineage.step_index)
            )
            if current is None:
                targets.append(target)
                continue
            draft_default = replace(
                target.default_row,
                spend_time=current.spend_time,
                unit_price=current.unit_price,
                unit_type=current.unit_type,
                units=current.units,
                base_fee=current.base_fee,
                discount=current.discount,
                testing_fee=current.testing_fee,
            )
            targets.append(replace(target, default_row=draft_default))
        return tuple(targets)

    def _save_promoted_draft(
        self,
        command: PromoteMatrixFeeRebaseCommand,
        edited_values: FeeEvaluationEditedExportValues,
    ) -> FeeEvaluationPricingDraftSnapshot:
        persisted = persist_current_v2_pricing_draft(
            persistence_service=self._pricing_draft_persistence_service,
            project_id=command.project_id,
            edited_values=edited_values,
        )
        if persisted is not None:
            return persisted
        new_version = command.new_confirmed_matrix.version
        existing = self._pricing_draft_store.get_by_context(
            project_id=command.project_id,
            confirmed_matrix_id=new_version.confirmed_matrix_id,
            confirmed_revision=new_version.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
        )
        now = datetime.now(timezone.utc).isoformat()
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=existing.draft_edit_id if existing else uuid4().hex,
            project_id=command.project_id,
            confirmed_matrix_id=new_version.confirmed_matrix_id,
            confirmed_revision=new_version.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
            edited_values=edited_values,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        return self._pricing_draft_store.upsert_current(snapshot)

    def _save_default_draft(
        self,
        *,
        project_id: str,
        new_confirmed_matrix: ConfirmedMatrixSnapshot,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot:
        existing = self._pricing_draft_store.get_by_context(
            project_id=project_id,
            confirmed_matrix_id=new_confirmed_matrix.version.confirmed_matrix_id,
            confirmed_revision=new_confirmed_matrix.version.confirmed_revision,
            fee_rule_version_id=fee_rule_version_id,
        )
        now = datetime.now(timezone.utc).isoformat()
        draft = ConfirmedMatrixFeeDraftService(
            confirmed_store=_SingleConfirmedMatrixStore(new_confirmed_matrix),
            contact_measurement_adapter=self._contact_measurement_adapter,
            contact_point_profile_adapter=self._contact_point_profile_adapter,
        ).build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id=project_id))
        values = edited_values_from_fee_draft(draft)
        persisted = persist_current_v2_pricing_draft(
            persistence_service=self._pricing_draft_persistence_service,
            project_id=project_id,
            edited_values=values,
        )
        if persisted is not None:
            return persisted
        snapshot = FeeEvaluationPricingDraftSnapshot(
            draft_edit_id=existing.draft_edit_id if existing else uuid4().hex,
            project_id=project_id,
            confirmed_matrix_id=new_confirmed_matrix.version.confirmed_matrix_id,
            confirmed_revision=new_confirmed_matrix.version.confirmed_revision,
            fee_rule_version_id=fee_rule_version_id,
            edited_values=values,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        return self._pricing_draft_store.upsert_current(snapshot)

    def _confirm_default_fee(
        self,
        *,
        project_id: str,
        snapshot: FeeEvaluationPricingDraftSnapshot,
    ) -> ConfirmedFeeVersion | None:
        if self._confirmed_fee_store is None:
            return None
        latest = self._confirmed_fee_store.get_latest_by_project(project_id)
        if latest is not None and confirmed_fee_matches_snapshot(latest, snapshot):
            return latest
        versions = self._confirmed_fee_store.list_by_project(project_id)
        next_revision = (versions[-1].confirmed_fee_revision + 1) if versions else 1
        version = ConfirmedFeeVersion(
            confirmed_fee_id=uuid4().hex,
            project_id=project_id,
            confirmed_fee_revision=next_revision,
            confirmed_matrix_id=snapshot.confirmed_matrix_id,
            confirmed_revision=snapshot.confirmed_revision,
            fee_rule_version_id=snapshot.fee_rule_version_id,
            pricing_draft_edit_id=snapshot.draft_edit_id,
            pricing_effective_from=None,
            summary=summary_from_edited_values(snapshot.edited_values),
            pricing_snapshot_json=(
                encode_confirmed_fee_pricing_snapshot(
                    snapshot=snapshot,
                    edited_values=active_only_edited_values(snapshot.edited_values),
                )
                if snapshot.generation is not None
                else edited_values_to_json(active_only_edited_values(snapshot.edited_values))
            ),
            confirmed_by="ConnLab Auto",
            confirmed_at=datetime.now(timezone.utc).isoformat(),
            confirmation_note=AUTO_REBASE_FEE_CONFIRMATION_NOTE,
        )
        return self._confirmed_fee_store.create(version)

def remap_rebase_result_to_confirmed_matrix(
    *,
    rebase_result: MatrixFeeRebaseResult,
    previous_pricing_draft: FeeEvaluationPricingDraftSnapshot | None,
    new_confirmed_matrix: ConfirmedMatrixSnapshot,
) -> FeeEvaluationEditedExportValues:
    """Project rebased rows onto the new Confirmed Matrix basic-fill identity."""
    basic_fill = build_basic_fill_from_confirmed_snapshot(new_confirmed_matrix)
    line_by_draft_identity = index_new_basic_fill_by_draft_identity(
        new_confirmed_matrix
    )
    rows = tuple(
        remap_row(row, line_by_draft_identity)
        for row in rebase_result.active_rows
    )
    manual_rows = tuple(
        remap_manual_row(row, new_confirmed_matrix) for row in rebase_result.manual_rows
    )
    values = FeeEvaluationEditedExportValues(
        rows=rows,
        summary=(
            previous_pricing_draft.edited_values.summary
            if previous_pricing_draft is not None
            else blank_summary()
        ),
        manual_rows=manual_rows,
        inactive_rows=tuple(
            _inactive_row_from_removed(row)
            for row in rebase_result.inactive_removed_rows
        ),
    )
    edited_row_lookup(values, basic_fill)
    validate_supported_manual_rows(values.manual_rows, basic_fill)
    return values


def _inactive_row_from_removed(
    row: MatrixFeeInactiveRemovedRow,
) -> FeeEvaluationEditedInactiveRow:
    """Convert one removed rebase row to hidden Fee draft recovery data."""
    return FeeEvaluationEditedInactiveRow(
        previous_row=row.previous_row,
        rebase_key=FeeEvaluationEditedInactiveRowKey(
            group_identity=row.rebase_key.group_identity,
            row_identity=row.rebase_key.row_identity,
            step_token=row.rebase_key.step_token,
            step_index=row.rebase_key.step_index,
        ),
        group_key=row.previous_group_key,
        group_label=row.previous_group_label,
        group_signature=row.previous_row_signature,
        inactive_reason=row.inactive_reason,
    )


def _pending_matches_command(
    pending: MatrixFeePendingRebaseSnapshot | None,
    command: PromoteMatrixFeeRebaseCommand,
) -> bool:
    if pending is None:
        return False
    previous = command.previous_confirmed_matrix.version
    return (
        pending.project_id == command.project_id
        and pending.project_matrix_draft_id
        == command.saved_matrix_draft.record.project_matrix_draft_id
        and pending.base_confirmed_matrix_id == previous.confirmed_matrix_id
        and pending.base_confirmed_revision == previous.confirmed_revision
        and pending.fee_rule_version_id == command.fee_rule_version_id
        and pending.matrix_draft_payload_signature
        == command.saved_matrix_draft_payload_signature
    )


class _SingleConfirmedMatrixStore:
    """Tiny adapter so the existing Fee Draft service can build from a fresh snapshot."""

    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self._snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self._snapshot.version.project_id != project_id:
            return None
        return self._snapshot
