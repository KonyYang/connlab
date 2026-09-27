from __future__ import annotations

from dataclasses import replace
from datetime import date
from types import SimpleNamespace

import pytest

from backend.application.matrix_editor_session_service import (
    MatrixEditorSessionActiveChangedError,
    MatrixEditorSessionCell,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionDraftDiscardCommand,
    MatrixEditorSessionDraftConflictError,
    MatrixEditorSessionDraftSaveCommand,
    MatrixEditorSessionError,
    MatrixEditorSessionGroup,
    MatrixEditorSessionRow,
    MatrixEditorSessionService,
    SOURCE_UNAVAILABLE_MESSAGE,
    _build_signature_from_project_draft,
)
from backend.application.matrix_fee_draft_rebase_service import MatrixFeeRebaseSummary
from backend.application.matrix_fee_pending_rebase_service import (
    MatrixFeePendingRebaseResult,
)
from backend.application.matrix_fee_rebase_promotion_service import (
    MatrixFeeRebasePromotionResult,
)
from backend.application.matrix_import_commit_service import MatrixImportCommitResult
from backend.application.matrix_import_method_authority import (
    MatrixImportMethodAuthoritySummary,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStepQuantity,
    ProjectMatrixDraftStatus,
    ProjectStatus,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)
from backend.domain.matrix_contact_measurement_models import (
    MatrixPointCategory,
    MatrixPointProfile,
    MatrixStepPointCategory,
    MatrixStepPointOverride,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import EffectiveConfirmedPointProfile
from backend.application.matrix_test_points_authority import validate_matrix_point_targets
from backend.application.confirmed_matrix_authority_service import (
    ConfirmProjectMatrixDraftCommand, ConfirmedMatrixAuthorityService,
    _build_confirmed_snapshot,
)


class _LegacyProfileAdapter:
    def __init__(self, profile: EffectiveConfirmedPointProfile) -> None:
        self.profile = profile

    def get_effective(self, project_id: str) -> EffectiveConfirmedPointProfile:
        assert project_id == "P1"
        return self.profile


def _legacy_profile(expression: str | None) -> EffectiveConfirmedPointProfile:
    return EffectiveConfirmedPointProfile(
        status="confirmed", readings_per_sample="2", revision_id="legacy-1",
        revision_sequence=1, fingerprint="legacy-hash", lineage="legacy", message=None,
        categories=({"category_id": "c1", "record_prefix": "HP", "included": True,
                     "count_per_sample": 2, "point_expression": expression},),
        cr_category_ids=(), delta_r_enabled=True,
    )


def test_seed_prefills_only_explicit_legacy_point_ids() -> None:
    service = _service(active=_build_active_snapshot(), source_snapshot=None,
                       point_profile_adapter=_LegacyProfileAdapter(_legacy_profile("1,3")))
    seed = service.get_seed(project_id="P1")
    assert seed.editor_draft is not None
    assert seed.editor_draft.point_profile == MatrixPointProfile(
        categories=(MatrixPointCategory("HP", "1,3", True),), delta_r_enabled=True,
    )
    assert seed.point_profile_warning is None
    assert seed.point_profile_prefilled_from_legacy is True


def test_seed_never_promotes_legacy_count_to_contiguous_ids() -> None:
    service = _service(active=_build_active_snapshot(), source_snapshot=None,
                       point_profile_adapter=_LegacyProfileAdapter(_legacy_profile(None)))
    seed = service.get_seed(project_id="P1")
    assert seed.editor_draft is not None
    assert seed.editor_draft.point_profile is None
    assert "without explicit point IDs" in (seed.point_profile_warning or "")
    assert seed.point_profile_prefilled_from_legacy is False


@pytest.mark.parametrize("test_item", (
    "CR at Specified Current (HP contacts only)",
    "CR at rated current HP/LP Contacts only",
))
def test_cr_named_steps_accept_narrower_point_exception(test_item: str) -> None:
    profile = MatrixPointProfile((MatrixPointCategory("HP", "1-4", True),))
    override = MatrixStepPointOverride(
        "group-1", "row-1", 1, "", (MatrixStepPointCategory("HP", "1-2"),),
    )

    validate_matrix_point_targets(
        (override,), profile=profile,
        groups=(SimpleNamespace(draft_group_id="group-1", is_selected=True),),
        rows=(SimpleNamespace(draft_row_id="row-1", test_item=test_item, is_sample_row=False),),
        cells=(SimpleNamespace(draft_group_id="group-1", draft_row_id="row-1", cell_value="1"),),
    )


def test_matrix_point_profile_subsets_are_checked_before_confirmation() -> None:
    service = _service(active=_build_active_snapshot(), source_snapshot=None)
    command = _confirm_saved_revision_command(_saved_revision_draft())
    profile = MatrixPointProfile(
        categories=(MatrixPointCategory(prefix="HP", point_expression="1,3", cr_selected=True),),
        delta_r_enabled=True,
    )
    override = MatrixStepPointOverride(
        draft_group_id="dg-1", draft_row_id="dr-1", step_sequence=1,
        step_suffix_note="", categories=(MatrixStepPointCategory(prefix="HP", point_expression="2"),),
    )

    with pytest.raises(MatrixEditorSessionError, match="outside the project Point Profile"):
        service.confirm_session(replace(command, point_profile=profile, point_overrides=(override,)))


def test_cr_step_rejects_exception_using_category_not_selected_for_cr() -> None:
    service = _service(active=_build_active_snapshot(), source_snapshot=None)
    command = _confirm_saved_revision_command(_saved_revision_draft())
    profile = MatrixPointProfile((
        MatrixPointCategory("SIG", "1-2", False), MatrixPointCategory("PWR", "1", True),
    ))
    override = MatrixStepPointOverride(
        "dg-1", "dr-1", 1, "", (MatrixStepPointCategory("SIG", "1"),),
    )

    with pytest.raises(MatrixEditorSessionError, match="not selected for CR"):
        service.confirm_session(replace(command, point_profile=profile, point_overrides=(override,)))


def test_first_matrix_confirmation_carries_saved_point_authority() -> None:
    draft = _saved_revision_draft()
    profile = MatrixPointProfile((MatrixPointCategory("SIG", "1-2", True),))
    overrides = (MatrixStepPointOverride(
        "dg-1", "dr-1", 1, "", (MatrixStepPointCategory("SIG", "2"),),
    ),)
    draft = replace(draft, record=replace(
        draft.record, point_profile=profile, point_overrides=overrides,
    ))

    snapshot = _build_confirmed_snapshot(
        draft=draft, selected_groups=draft.groups, confirmed_by="operator",
    )

    assert snapshot.version.point_profile == profile
    assert snapshot.version.point_overrides == overrides


def test_first_confirmation_persists_canonical_point_authority_not_raw_draft() -> None:
    draft = _saved_revision_draft()
    raw_profile = MatrixPointProfile((MatrixPointCategory(" SIG ", "1,2,3", True),))
    raw_overrides = (MatrixStepPointOverride(
        "dg-1", "dr-1", 1, " ", (MatrixStepPointCategory(" SIG ", "2,3"),),
    ),)
    draft = replace(draft, record=replace(
        draft.record, point_profile=raw_profile, point_overrides=raw_overrides,
    ))
    service = ConfirmedMatrixAuthorityService(
        project_store=SimpleNamespace(get=lambda _id: object()),
        draft_store=SimpleNamespace(get=lambda _id: draft),
        confirmed_store=SimpleNamespace(
            get_active_by_project=lambda _id: None,
            create_snapshot=lambda snapshot: snapshot,
        ),
    )

    confirmed = service.confirm_draft(ConfirmProjectMatrixDraftCommand(
        project_id="P1", project_matrix_draft_id="pmd-edit", confirmed_by="operator",
    ))

    assert confirmed.version.point_profile == MatrixPointProfile((
        MatrixPointCategory("SIG", "1-3", True),
    ))
    assert confirmed.version.point_overrides == (MatrixStepPointOverride(
        "dg-1", "dr-1", 1, "", (MatrixStepPointCategory("SIG", "2-3"),),
    ),)
    assert draft.record.point_profile == raw_profile


def test_get_seed_when_source_snapshot_missing_returns_unavailable_message() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    seed = service.get_seed(project_id="P1")
    assert seed.active_confirmed_matrix_id == "cmv-1"
    assert seed.editor_draft is not None
    assert seed.source_status == "unavailable"
    assert seed.source_unavailable_message == SOURCE_UNAVAILABLE_MESSAGE
    assert seed.source_preview_payload is None


def test_get_seed_rebuilt_source_preview_payload_preserves_row_mcr() -> None:
    active = _build_active_snapshot()
    source_snapshot = SourceMatrixSnapshot(
        snapshot_id="sms-1",
        import_id="smi-1",
        project_id="P1",
        source_table_index=1,
        rows=(
            SourceMatrixRowSnapshot(
                row_snapshot_id="sr-1",
                row_order=1,
                source_row_index=3,
                test_item="Contact Resistance (Low Level)",
                source_section="6.1",
                method="EIA-364-23D",
                condition="20mV max, 100mA max",
                requirement="Initial <= 0.25 milliohms",
            ),
        ),
        groups=(
            SourceMatrixGroupSnapshot(
                group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression="5",
            ),
        ),
        cells=(
            SourceMatrixCellSnapshot(
                cell_snapshot_id="sc-1",
                row_snapshot_id="sr-1",
                group_snapshot_id="sg-1",
                cell_value="1",
            ),
        ),
        created_at="2026-05-27T00:00:00Z",
    )
    service = _service(active=active, source_snapshot=source_snapshot)

    seed = service.get_seed(project_id="P1")

    assert seed.source_preview_payload is not None
    row = seed.source_preview_payload["rows"][0]
    assert row["method"] == "EIA-364-23D"
    assert row["condition"] == "20mV max, 100mA max"
    assert row["requirement"] == "Initial <= 0.25 milliohms"


def test_get_seed_restores_latest_source_replacement_draft() -> None:
    active = _build_active_snapshot()
    replacement_draft = _source_replacement_draft()
    replacement_source = _source_replacement_snapshot()
    service = _service(
        active=active,
        source_snapshot=None,
        source_store=_MappedSourceStore(
            imports={"smi-2": _source_replacement_import()},
            snapshots={"sms-2": replacement_source},
        ),
        draft_store=_CurrentDraftStore(replacement_draft),
    )

    seed = service.get_seed(project_id="P1")

    assert seed.active_confirmed_matrix_id == "cmv-1"
    assert seed.active_source_import_id == "smi-1"
    assert seed.editor_draft_id == "pmd-replacement"
    assert seed.editor_draft is not None
    assert seed.editor_draft.rows[0].test_item == "Imported replacement row"
    assert seed.editor_source_import_id == "smi-2"
    assert seed.editor_source_snapshot_id == "sms-2"
    assert seed.loaded_source == "draft"
    assert seed.source_preview_payload is not None
    assert seed.source_preview_payload["source_document_name"] == "replacement.docx"


def test_get_seed_restores_unconfirmed_import_draft() -> None:
    replacement_draft = _source_replacement_draft()
    service = _service(
        active=None,
        source_snapshot=None,
        source_store=_MappedSourceStore(
            imports={"smi-2": _source_replacement_import()},
            snapshots={"sms-2": _source_replacement_snapshot()},
        ),
        draft_store=_CurrentDraftStore(replacement_draft),
    )

    seed = service.get_seed(project_id="P1")

    assert seed.active_confirmed_matrix_id is None
    assert seed.editor_draft_id == "pmd-replacement"
    assert seed.editor_source_import_id == "smi-2"
    assert seed.loaded_source == "draft"


def test_get_seed_ignores_source_draft_older_than_active_authority() -> None:
    active = _build_active_snapshot()
    replacement_draft = _source_replacement_draft()
    historical_record = replace(
        replacement_draft.record,
        updated_at="2026-05-26T23:59:59Z",
    )
    service = _service(
        active=active,
        source_snapshot=None,
        draft_store=_CurrentDraftStore(
            replace(replacement_draft, record=historical_record)
        ),
    )

    seed = service.get_seed(project_id="P1")

    assert seed.editor_draft_id is None
    assert seed.editor_source_import_id == "smi-1"
    assert seed.loaded_source == "authority"


def test_confirm_session_no_change_returns_http200_semantics() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        post_test_buffer_days="0",
        planned_test_start_date="2026-09-01",
        planned_test_complete_date="2026-09-01",
        estimated_completion_date="2026-09-01",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None
    assert result.fee_rebase_promotion_status == "not_required"


def test_confirm_session_rejects_duplicate_group_keys_before_signature_comparison() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = _confirm_saved_revision_command(_saved_revision_draft())
    duplicate_group = replace(
        command.groups[0],
        draft_group_id="duplicate-group",
        source_group_snapshot_id=None,
        group_order=2,
    )

    with pytest.raises(MatrixEditorSessionError, match="Duplicate Matrix group key: g1"):
        service.confirm_session(replace(command, groups=(*command.groups, duplicate_group)))


def test_save_editor_draft_attaches_current_fee_rebase_status() -> None:
    active = _build_active_snapshot()
    pending = _RecordingPendingFeeRebaseService(
        MatrixFeePendingRebaseResult(
            status="current",
            summary=MatrixFeeRebaseSummary(
                preserved_count=1,
                added_count=2,
                removed_count=0,
            ),
        )
    )
    service = _service(
        active=active,
        source_snapshot=None,
        draft_persistence_service=_RecordingDraftPersistenceService(),
        matrix_revision_flow_service=_RecordingMatrixRevisionFlowService(),
        pending_fee_rebase_service=pending,
    )

    result = service.save_editor_draft(_save_command())

    assert result.editor_draft_id == "pmd-rev"
    assert result.fee_rebase_status == "current"
    assert result.fee_rebase_summary == MatrixFeeRebaseSummary(
        preserved_count=1,
        added_count=2,
        removed_count=0,
    )
    assert pending.rebase_command is not None
    assert pending.rebase_command.saved_matrix_draft.record.project_matrix_draft_id == "pmd-rev"


def test_save_editor_draft_rejects_duplicate_group_keys_before_creating_revision() -> None:
    service = _service(active=_build_active_snapshot(), source_snapshot=None)
    command = _save_command()
    duplicate_group = replace(
        command.groups[0],
        draft_group_id="duplicate-group",
        source_group_snapshot_id=None,
        group_order=2,
    )

    with pytest.raises(MatrixEditorSessionError, match="Duplicate Matrix group key: g1"):
        service.save_editor_draft(replace(command, groups=(*command.groups, duplicate_group)))


def test_save_editor_draft_keeps_matrix_success_when_fee_rebase_failed() -> None:
    pending = _RecordingPendingFeeRebaseService(
        MatrixFeePendingRebaseResult(
            status="failed",
            error="Fee rebase failed after Matrix autosave: pricing context exploded",
        )
    )
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_persistence_service=_RecordingDraftPersistenceService(),
        matrix_revision_flow_service=_RecordingMatrixRevisionFlowService(),
        pending_fee_rebase_service=pending,
    )

    result = service.save_editor_draft(_save_command())

    assert result.draft_status == "current"
    assert result.fee_rebase_status == "failed"
    assert "pricing context exploded" in (result.fee_rebase_error or "")


def test_confirm_saved_revision_attaches_fee_rebase_promotion_status() -> None:
    draft = _saved_revision_draft()
    promotion = _RecordingFeeRebasePromotionService(
        MatrixFeeRebasePromotionResult(
            status="promoted",
            summary=MatrixFeeRebaseSummary(
                preserved_count=1,
                added_count=0,
                removed_count=0,
            ),
        )
    )
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_SavedDraftStore(draft),
        fee_rebase_promotion_service=promotion,
    )

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.fee_rebase_promotion_status == "promoted"
    assert result.fee_rebase_promotion_summary == MatrixFeeRebaseSummary(
        preserved_count=1,
        added_count=0,
        removed_count=0,
    )
    assert promotion.command is not None
    assert promotion.command.saved_matrix_draft == draft
    assert promotion.command.saved_matrix_draft_payload_signature == (
        _build_signature_from_project_draft(draft)
    )
    assert promotion.command.previous_confirmed_matrix.version.confirmed_matrix_id == "cmv-1"
    assert promotion.command.new_confirmed_matrix is result.confirmed_snapshot


def test_confirm_saved_revision_keeps_published_when_fee_promotion_failed() -> None:
    draft = _saved_revision_draft()
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_SavedDraftStore(draft),
        fee_rebase_promotion_service=_RecordingFeeRebasePromotionService(
            MatrixFeeRebasePromotionResult(
                status="failed",
                error="Fee rebase promotion failed: database unavailable",
            )
        ),
    )

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.confirmed_snapshot is not None
    assert result.fee_rebase_promotion_status == "failed"
    assert "database unavailable" in (result.fee_rebase_promotion_error or "")


def test_confirm_session_publishes_contact_plan_only_saved_revision() -> None:
    draft = _saved_revision_draft()
    contact_plan = MatrixStepContactPlan(
        contact_kind="llcr",
        coverage_status="eligible",
        included=True,
        exclusion_reason=None,
        is_override=False,
        readings_per_sample="33",
        families=(
            MatrixStepContactFamily(
                family_id="high_power_pin",
                family_label="High Power Pin",
                count_per_sample="4",
                record_label="High Power Pin contact",
                record_prefix="HP",
                included=True,
                is_custom=False,
            ),
        ),
    )
    draft = replace(
        draft,
        step_quantities=(
            ProjectMatrixDraftStepQuantity(
                draft_step_quantity_id="quantity-1",
                project_matrix_draft_id=draft.record.project_matrix_draft_id,
                draft_group_id=draft.groups[0].draft_group_id,
                draft_row_id=draft.rows[0].draft_row_id,
                step_sequence=1,
                step_suffix_note=None,
                raw_token="1",
                test_points_per_sample="33",
                readings_per_point="1",
                contact_points_per_sample="33",
                source="matrix_contact_plan",
                review_required=False,
                review_reason=None,
                updated_at="2026-07-11T10:00:00+00:00",
                contact_plan=contact_plan,
            ),
        ),
    )
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_SavedDraftStore(draft),
    )

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.confirmed_snapshot is not None
    assert result.confirmed_snapshot.version.confirmed_revision == 2
    assert result.confirmed_snapshot.step_quantities[0].contact_plan == contact_plan
    assert result.confirmed_snapshot.step_quantities[0].contact_points_per_sample == "33"


def test_confirm_session_publishes_profile_only_saved_revision() -> None:
    draft = _saved_revision_draft()
    profile = MatrixPointProfile(
        categories=(MatrixPointCategory(prefix="HP", point_expression="1,3", cr_selected=True),),
        delta_r_enabled=False,
    )
    draft = replace(draft, record=replace(draft.record, point_profile=profile))
    service = _service(active=_build_active_snapshot(), source_snapshot=None,
                       draft_store=_SavedDraftStore(draft))

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.confirmed_snapshot is not None
    assert result.confirmed_snapshot.version.point_profile == profile


def test_confirm_session_publishes_matrix_equal_revision_when_contact_plan_changes() -> None:
    contact_plan = MatrixStepContactPlan(
        contact_kind="llcr",
        coverage_status="eligible",
        included=True,
        exclusion_reason=None,
        is_override=False,
        readings_per_sample="4",
        families=(
            MatrixStepContactFamily(
                family_id="high_power_pin",
                family_label="High Power Pin",
                count_per_sample="4",
                record_label="High Power Pin contact",
                record_prefix="HP",
                included=True,
                is_custom=False,
            ),
        ),
    )
    draft = _matrix_equal_saved_revision_draft(contact_plan)
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_SavedDraftStore(draft),
    )

    result = service.confirm_session(_confirm_saved_revision_command(draft))

    assert result.publish_status == "published"
    assert result.confirmed_snapshot is not None
    assert result.confirmed_snapshot.version.confirmed_revision == 2
    assert result.confirmed_snapshot.step_quantities[0].contact_plan == contact_plan


def test_confirm_first_authority_initializes_default_fee_authority() -> None:
    promotion = _RecordingFeeRebasePromotionService(
        MatrixFeeRebasePromotionResult(status="default_promoted")
    )
    service = _service(
        active=None,
        source_snapshot=None,
        draft_persistence_service=_RecordingDraftPersistenceService(),
        matrix_import_commit_service=_RecordingMatrixImportCommitService(),
        confirmed_matrix_authority_service=_RecordingConfirmedAuthorityService(),
        fee_rebase_promotion_service=promotion,
    )

    result = service.confirm_session(_first_confirm_command())

    assert result.publish_status == "published"
    assert result.confirmed_snapshot is not None
    assert result.fee_rebase_promotion_status == "default_promoted"
    assert promotion.initial_project_id == "P1"
    assert promotion.initial_confirmed_matrix is result.confirmed_snapshot


@pytest.mark.parametrize("schedule", [
    {"planned_test_start_date": None},
    {"planned_test_complete_date": ""},
    {"estimated_completion_date": None},
])
def test_first_matrix_confirm_rejects_incomplete_plan(schedule) -> None:
    service = _service(
        active=None, source_snapshot=None,
        draft_persistence_service=_RecordingDraftPersistenceService(),
        matrix_import_commit_service=_RecordingMatrixImportCommitService(),
        confirmed_matrix_authority_service=_RecordingConfirmedAuthorityService(),
    )
    with pytest.raises(MatrixEditorSessionError, match="is required"):
        service.confirm_session(replace(_first_confirm_command(), **schedule))


def test_discard_editor_draft_deletes_pending_fee_rebase() -> None:
    draft_store = _DiscardDraftStore(_active_editor_draft())
    pending = _RecordingPendingFeeRebaseService(MatrixFeePendingRebaseResult(status="not_required"))
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=draft_store,
        pending_fee_rebase_service=pending,
    )

    result = service.discard_editor_draft(
        MatrixEditorSessionDraftDiscardCommand(project_id="P1")
    )

    assert result.discarded is True
    assert pending.deleted_matrix_draft_id == "pmd-edit"


def test_discard_editor_draft_uses_expected_import_draft_id() -> None:
    imported_draft = _source_replacement_draft()
    historical_draft = replace(
        imported_draft,
        record=replace(imported_draft.record, updated_at="2026-05-26T23:59:59Z"),
    )
    draft_store = _DiscardDraftStore(historical_draft)
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=draft_store,
    )

    result = service.discard_editor_draft(
        MatrixEditorSessionDraftDiscardCommand(
            project_id="P1",
            expected_editor_draft_id="pmd-replacement",
            expected_saved_payload_signature=_build_signature_from_project_draft(
                historical_draft
            ),
        )
    )

    assert result.discarded is True
    assert draft_store.deleted == "pmd-replacement"


def test_discard_editor_draft_deletes_unconfirmed_import_draft() -> None:
    imported_draft = _source_replacement_draft()
    draft_store = _DiscardDraftStore(imported_draft)
    service = _service(
        active=None,
        source_snapshot=None,
        draft_store=draft_store,
    )

    result = service.discard_editor_draft(
        MatrixEditorSessionDraftDiscardCommand(
            project_id="P1",
            expected_editor_draft_id="pmd-replacement",
            expected_saved_payload_signature=_build_signature_from_project_draft(
                imported_draft
            ),
        )
    )

    assert result.discarded is True
    assert result.active_confirmed_matrix_id is None
    assert draft_store.deleted == "pmd-replacement"


def test_discard_editor_draft_surfaces_pending_delete_failure() -> None:
    pending = _FailingPendingFeeRebaseService()
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_DiscardDraftStore(_active_editor_draft()),
        pending_fee_rebase_service=pending,
    )

    with pytest.raises(MatrixEditorSessionDraftConflictError, match="pending Fee rebase"):
        service.discard_editor_draft(
            MatrixEditorSessionDraftDiscardCommand(project_id="P1")
        )


def test_discard_editor_draft_deletes_pending_again_after_matrix_delete_race() -> None:
    pending = _RacePendingFeeRebaseService()
    service = _service(
        active=_build_active_snapshot(),
        source_snapshot=None,
        draft_store=_DiscardDraftStore(_active_editor_draft()),
        pending_fee_rebase_service=pending,
    )

    result = service.discard_editor_draft(
        MatrixEditorSessionDraftDiscardCommand(project_id="P1")
    )

    assert result.discarded is True
    assert pending.delete_calls == 2
    assert pending.pending_exists is False


def test_confirm_session_no_change_ignores_unselected_source_groups() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        post_test_buffer_days="0",
        planned_test_start_date="2026-09-01",
        planned_test_complete_date="2026-09-01",
        estimated_completion_date="2026-09-01",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
            MatrixEditorSessionGroup(
                draft_group_id="dg-2",
                source_group_snapshot_id="sg-2",
                group_order=2,
                group_key="g2",
                group_label="2",
                is_selected=False,
                sample_quantity_expression=None,
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-2",
                cell_value="2",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_treats_group_prefix_as_same_signature() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        post_test_buffer_days="0",
        planned_test_start_date="2026-09-01",
        planned_test_complete_date="2026-09-01",
        estimated_completion_date="2026-09-01",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="Group 1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_when_active_id_changed_raises_conflict_message() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-old",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="2",
            ),
        ),
    )
    with pytest.raises(MatrixEditorSessionActiveChangedError) as exc:
        service.confirm_session(command)
    assert "Matrix was updated. Reload the latest Matrix to continue." in str(exc.value)


def test_confirm_session_rejects_selected_group_sample_without_digit() -> None:
    active = _build_active_snapshot(sample_quantity_expression="")
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id="smi-1",
        source_snapshot_id="sms-1",
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="sample only",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    with pytest.raises(MatrixEditorSessionError) as exc:
        service.confirm_session(command)
    assert "Sample quantity is required for selected groups: 1." in str(exc.value)


class _ProjectStore:
    def get(self, project_id: str):
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-05-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.LTR_REGISTERED,
            created_on=date(2026, 5, 22),
        )


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self._active = active

    def get_active_by_project(self, project_id: str):
        return self._active if project_id == "P1" else None

    def list_by_project(self, project_id: str):
        return (self._active,) if project_id == "P1" and self._active is not None else ()

    def supersede_active_and_create_snapshot(self, *, previous_active_confirmed_matrix_id: str, snapshot, superseded_reason=None):
        self._active = snapshot
        return snapshot


class _SourceStore:
    def __init__(self, *, source_snapshot) -> None:
        self._snapshot = source_snapshot
        self._import = SourceMatrixImportRecord(
            import_id="smi-1",
            project_id="P1",
            draft_id="ptpd-1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            import_status=SourceMatrixImportStatus.IMPORTED,
            source_spec_number=None,
            source_spec_revision=None,
            parse_time="2026-05-27T00:00:00Z",
            parser_version="parser-v1",
            payload_schema_version="1.0",
            warnings=(),
            blockers=(),
            selected_group_keys_at_import=("g1",),
            task261_commit_fingerprint=None,
            created_at="2026-05-27T00:00:00Z",
        )

    def get_import(self, import_id: str):
        return self._import if import_id == "smi-1" else None

    def get_snapshot(self, snapshot_id: str):
        return self._snapshot if snapshot_id == "sms-1" else None


class _MappedSourceStore:
    def __init__(self, *, imports, snapshots) -> None:
        self._imports = imports
        self._snapshots = snapshots

    def get_import(self, import_id: str):
        return self._imports.get(import_id)

    def get_snapshot(self, snapshot_id: str):
        return self._snapshots.get(snapshot_id)


class _DraftStore:
    def get(self, project_matrix_draft_id: str):
        return None

    def list_by_project(self, project_id: str):
        return ()

    def delete(self, project_matrix_draft_id: str):
        return None

    def get_by_project_and_base_confirmed_matrix(self, project_id: str, base_confirmed_matrix_id: str):
        return None

    def get_by_project_and_source_import(self, project_id: str, source_import_id: str):
        return None


class _CurrentDraftStore(_DraftStore):
    def __init__(self, draft: ProjectMatrixDraftSnapshot) -> None:
        self._draft = draft

    def get(self, project_matrix_draft_id: str):
        if project_matrix_draft_id == self._draft.record.project_matrix_draft_id:
            return self._draft
        return None

    def list_by_project(self, project_id: str):
        return [self._draft.record] if project_id == self._draft.record.project_id else []

    def get_by_project_and_source_import(self, project_id: str, source_import_id: str):
        record = self._draft.record
        if project_id == record.project_id and source_import_id == record.source_import_id:
            return record
        return None


class _DiscardDraftStore(_DraftStore):
    def __init__(self, draft: ProjectMatrixDraftSnapshot | None) -> None:
        self._draft = draft
        self.deleted: str | None = None

    def get(self, project_matrix_draft_id: str):
        if self._draft is None:
            return None
        return self._draft if project_matrix_draft_id == self._draft.record.project_matrix_draft_id else None

    def list_by_project(self, project_id: str):
        return [self._draft.record] if self._draft is not None else []

    def delete(self, project_matrix_draft_id: str):
        self.deleted = project_matrix_draft_id
        self._draft = None
        return True


class _SavedDraftStore(_DraftStore):
    def __init__(self, draft: ProjectMatrixDraftSnapshot) -> None:
        self._draft = draft

    def get(self, project_matrix_draft_id: str):
        if project_matrix_draft_id == self._draft.record.project_matrix_draft_id:
            return self._draft
        return None


class _DraftPersistenceService:
    def update_draft(self, command):
        raise AssertionError("update_draft should not be called in no-change tests")


class _MatrixImportCommitService:
    def commit(self, command):
        raise AssertionError("commit should not be called in no-change tests")


class _RecordingMatrixImportCommitService:
    def __init__(self) -> None:
        self.draft = _saved_revision_draft()

    def commit(self, command):
        return MatrixImportCommitResult(
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            selected_group_keys_committed=("g1",),
            commit_status="committed",
            project_matrix_draft=self.draft,
            method_authority_sync=MatrixImportMethodAuthoritySummary(
                status="current",
                updated_count=0,
                current_count=1,
                review_count=0,
                standard_resource_id=None,
                effective_worksheet_name=None,
                catalog_fingerprint=None,
                context_fingerprint="test-context",
                rows=(),
            ),
        )


class _MatrixRevisionFlowService:
    def create_revision_draft(self, command):
        raise AssertionError("create_revision_draft should not be called in no-change tests")

    def confirm_revision_draft(self, command):
        raise AssertionError("confirm_revision_draft should not be called in no-change tests")


class _RecordingMatrixRevisionFlowService:
    def __init__(self) -> None:
        self.confirm_revision_called = False

    def create_revision_draft(self, command):
        return ProjectMatrixDraftSnapshot(
            record=ProjectMatrixDraftRecord(
                project_matrix_draft_id="pmd-rev",
                project_id="P1",
                source_import_id=None,
                source_snapshot_id="sms-1",
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-27T00:00:00Z",
                updated_at="2026-05-27T00:00:00Z",
                base_confirmed_matrix_id="cmv-1",
            ),
            groups=(),
            rows=(),
            cells=(),
        )

    def confirm_revision_draft(self, command):
        self.confirm_revision_called = True
        raise AssertionError("Matrix Editor session confirm should not use legacy revision validation.")


class _RecordingDraftPersistenceService:
    def __init__(self) -> None:
        self.updated = False

    def update_draft(self, command):
        self.updated = True
        return ProjectMatrixDraftSnapshot(
            record=ProjectMatrixDraftRecord(
                project_matrix_draft_id=command.project_matrix_draft_id,
                project_id=command.project_id,
                source_import_id=None,
                source_snapshot_id="sms-1",
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-27T00:00:00Z",
                updated_at="2026-05-27T00:00:01Z",
                base_confirmed_matrix_id="cmv-1",
            ),
            groups=tuple(
                ProjectMatrixDraftGroup(
                    draft_group_id=group.draft_group_id,
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    source_group_snapshot_id=group.source_group_snapshot_id,
                    group_order=group.group_order,
                    group_key=group.group_key,
                    group_label=group.group_label,
                    is_selected=group.is_selected,
                    sample_quantity_expression=group.sample_quantity_expression,
                    sample_note=group.sample_note,
                )
                for group in command.groups
            ),
            rows=tuple(
                ProjectMatrixDraftRow(
                    draft_row_id=row.draft_row_id,
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    source_row_snapshot_id=row.source_row_snapshot_id,
                    row_order=row.row_order,
                    test_item=row.test_item,
                    source_section=row.source_section,
                    method=row.method,
                    condition=row.condition,
                    requirement=row.requirement,
                    is_sample_row=row.is_sample_row,
                )
                for row in command.rows
            ),
            cells=tuple(
                ProjectMatrixDraftCell(
                    draft_cell_id=f"cell-{index}",
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    draft_row_id=cell.draft_row_id,
                    draft_group_id=cell.draft_group_id,
                    cell_value=cell.cell_value,
                )
                for index, cell in enumerate(command.cells, start=1)
            ),
        )


class _ConfirmedAuthorityService:
    def confirm_draft(self, command):
        raise AssertionError("confirm_draft should not be called in no-change tests")


class _RecordingConfirmedAuthorityService:
    def confirm_draft(self, command):
        return _build_active_snapshot()


class _RecordingPendingFeeRebaseService:
    def __init__(self, result: MatrixFeePendingRebaseResult) -> None:
        self._result = result
        self.rebase_command = None
        self.deleted_matrix_draft_id: str | None = None

    def rebase_after_matrix_autosave(self, command):
        self.rebase_command = command
        return self._result

    def delete_for_matrix_draft(self, command):
        self.deleted_matrix_draft_id = command.project_matrix_draft_id
        return None


class _FailingPendingFeeRebaseService:
    def rebase_after_matrix_autosave(self, command):
        return MatrixFeePendingRebaseResult(status="not_required")

    def delete_for_matrix_draft(self, command):
        raise RuntimeError("storage busy")


class _RacePendingFeeRebaseService:
    def __init__(self) -> None:
        self.delete_calls = 0
        self.pending_exists = True

    def rebase_after_matrix_autosave(self, command):
        return MatrixFeePendingRebaseResult(status="not_required")

    def delete_for_matrix_draft(self, command):
        self.delete_calls += 1
        self.pending_exists = False
        if self.delete_calls == 1:
            self.pending_exists = True
        return None


class _RecordingFeeRebasePromotionService:
    def __init__(self, result: MatrixFeeRebasePromotionResult) -> None:
        self._result = result
        self.command = None
        self.initial_project_id = None
        self.initial_confirmed_matrix = None

    def promote_after_matrix_confirm(self, command):
        self.command = command
        return self._result

    def initialize_after_first_matrix_confirm(
        self,
        *,
        project_id,
        new_confirmed_matrix,
        fee_rule_version_id,
    ):
        self.initial_project_id = project_id
        self.initial_confirmed_matrix = new_confirmed_matrix
        return self._result


def _service(
    *,
    active: ConfirmedMatrixSnapshot | None,
    source_snapshot,
    source_store=None,
    draft_store=None,
    draft_persistence_service=None,
    matrix_import_commit_service=None,
    matrix_revision_flow_service=None,
    confirmed_matrix_authority_service=None,
    pending_fee_rebase_service=None,
    fee_rebase_promotion_service=None,
    point_profile_adapter=None,
):
    return MatrixEditorSessionService(
        project_store=_ProjectStore(),
        confirmed_store=_ConfirmedStore(active),
        source_store=source_store or _SourceStore(source_snapshot=source_snapshot),
        draft_store=draft_store or _DraftStore(),
        draft_persistence_service=draft_persistence_service or _DraftPersistenceService(),
        matrix_import_commit_service=matrix_import_commit_service
        or _MatrixImportCommitService(),
        matrix_revision_flow_service=matrix_revision_flow_service
        or _MatrixRevisionFlowService(),
        confirmed_matrix_authority_service=confirmed_matrix_authority_service
        or _ConfirmedAuthorityService(),
        pending_fee_rebase_service=pending_fee_rebase_service,
        fee_rebase_promotion_service=fee_rebase_promotion_service,
        point_profile_adapter=point_profile_adapter,
    )


def _save_command() -> MatrixEditorSessionDraftSaveCommand:
    return MatrixEditorSessionDraftSaveCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id="sms-1",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Contact Resistance",
                source_section="6.1",
                method="EIA-364-23D",
                condition="Initial",
                requirement="< 10 mohm",
                day_expression=None,
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )


def _active_editor_draft() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-edit",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-27T00:00:00Z",
            updated_at="2026-05-27T00:00:01Z",
            base_confirmed_matrix_id="cmv-1",
        ),
        groups=(),
        rows=(),
        cells=(),
    )


def _saved_revision_draft() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-edit",
            project_id="P1",
            source_import_id=None,
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-27T00:00:00Z",
            updated_at="2026-05-27T00:00:01Z",
            base_confirmed_matrix_id="cmv-1",
            post_test_buffer_days="0",
            planned_test_start_date="2026-09-01",
            planned_test_complete_date="2026-09-01",
            estimated_completion_date="2026-09-01",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="dg-1",
                project_matrix_draft_id="pmd-edit",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="dr-1",
                project_matrix_draft_id="pmd-edit",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Contact Resistance",
                source_section="6.1",
                method="EIA-364-23D",
                condition="Initial",
                requirement="< 10 mohm",
                is_sample_row=False,
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="dc-1",
                project_matrix_draft_id="pmd-edit",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )


def _source_replacement_draft() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-replacement",
            project_id="P1",
            source_import_id="smi-2",
            source_snapshot_id="sms-2",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-28T00:00:00Z",
            updated_at="2026-05-28T00:00:01Z",
            base_confirmed_matrix_id=None,
            post_test_buffer_days="0",
            planned_test_start_date="2026-09-01",
            planned_test_complete_date="2026-09-01",
            estimated_completion_date="2026-09-01",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="dg-2",
                project_matrix_draft_id="pmd-replacement",
                source_group_snapshot_id="sg-2",
                group_order=1,
                group_key="g2",
                group_label="H",
                is_selected=True,
                sample_quantity_expression="3",
                sample_note=None,
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="dr-2",
                project_matrix_draft_id="pmd-replacement",
                source_row_snapshot_id="sr-2",
                row_order=1,
                test_item="Imported replacement row",
                source_section="5.5",
                method="IEC 60512-1-1",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="dc-2",
                project_matrix_draft_id="pmd-replacement",
                draft_row_id="dr-2",
                draft_group_id="dg-2",
                cell_value="1",
            ),
        ),
    )


def _source_replacement_import() -> SourceMatrixImportRecord:
    return SourceMatrixImportRecord(
        import_id="smi-2",
        project_id="P1",
        draft_id="ptpd-2",
        source_document_path="C:/replacement.docx",
        source_document_name="replacement.docx",
        source_format=".docx",
        source_asset_id=None,
        source_case_id=None,
        source_draft_id=None,
        import_status=SourceMatrixImportStatus.IMPORTED,
        source_spec_number=None,
        source_spec_revision=None,
        parse_time="2026-05-28T00:00:00Z",
        parser_version="parser-v1",
        payload_schema_version="1.0",
        warnings=(),
        blockers=(),
        selected_group_keys_at_import=("g2",),
        task261_commit_fingerprint=None,
        created_at="2026-05-28T00:00:00Z",
    )


def _source_replacement_snapshot() -> SourceMatrixSnapshot:
    return SourceMatrixSnapshot(
        snapshot_id="sms-2",
        import_id="smi-2",
        project_id="P1",
        source_table_index=1,
        rows=(
            SourceMatrixRowSnapshot(
                row_snapshot_id="sr-2",
                row_order=1,
                source_row_index=1,
                test_item="Imported replacement row",
                source_section="5.5",
                method="IEC 60512-1-1",
                condition="10x min magnification",
                requirement="No detrimental condition",
            ),
        ),
        groups=(
            SourceMatrixGroupSnapshot(
                group_snapshot_id="sg-2",
                group_order=1,
                group_key="g2",
                group_label="H",
                sample_quantity_expression="3",
            ),
        ),
        cells=(
            SourceMatrixCellSnapshot(
                cell_snapshot_id="sc-2",
                row_snapshot_id="sr-2",
                group_snapshot_id="sg-2",
                cell_value="1",
            ),
        ),
        created_at="2026-05-28T00:00:00Z",
    )


def _matrix_equal_saved_revision_draft(
    contact_plan: MatrixStepContactPlan,
) -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-contact",
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-11T10:00:00+00:00",
            updated_at="2026-07-11T10:01:00+00:00",
            base_confirmed_matrix_id="cmv-1",
            post_test_buffer_days="0",
            planned_test_start_date="2026-09-01",
            planned_test_complete_date="2026-09-01",
            estimated_completion_date="2026-09-01",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="dg-1",
                project_matrix_draft_id="pmd-contact",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="dr-1",
                project_matrix_draft_id="pmd-contact",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="dc-contact",
                project_matrix_draft_id="pmd-contact",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
        step_quantities=(
            ProjectMatrixDraftStepQuantity(
                draft_step_quantity_id="quantity-contact",
                project_matrix_draft_id="pmd-contact",
                draft_group_id="dg-1",
                draft_row_id="dr-1",
                step_sequence=1,
                step_suffix_note=None,
                raw_token="1",
                test_points_per_sample="4",
                readings_per_point="1",
                contact_points_per_sample="4",
                source="matrix_contact_plan",
                review_required=False,
                review_reason=None,
                updated_at="2026-07-11T10:01:00+00:00",
                contact_plan=contact_plan,
            ),
        ),
    )


def _confirm_saved_revision_command(
    draft: ProjectMatrixDraftSnapshot,
) -> MatrixEditorSessionConfirmCommand:
    return MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id="sms-1",
        confirmed_by="operator",
        groups=tuple(
            MatrixEditorSessionGroup(
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=group.group_order,
                group_key=group.group_key,
                group_label=group.group_label,
                is_selected=group.is_selected,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note,
            )
            for group in draft.groups
        ),
        rows=tuple(
            MatrixEditorSessionRow(
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=row.row_order,
                test_item=row.test_item,
                source_section=row.source_section,
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
                is_sample_row=row.is_sample_row,
            )
            for row in draft.rows
        ),
        cells=tuple(
            MatrixEditorSessionCell(
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell.cell_value,
            )
            for cell in draft.cells
        ),
        expected_editor_draft_id=draft.record.project_matrix_draft_id,
        expected_saved_payload_signature=_build_signature_from_project_draft(draft),
        post_test_buffer_days=draft.record.post_test_buffer_days,
        planned_test_start_date=draft.record.planned_test_start_date,
        planned_test_complete_date=draft.record.planned_test_complete_date,
        estimated_completion_date=draft.record.estimated_completion_date,
    )


def _first_confirm_command() -> MatrixEditorSessionConfirmCommand:
    draft = _saved_revision_draft()
    return MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id=None,
        expected_active_confirmed_revision=None,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id="sms-1",
        confirmed_by="operator",
        post_test_buffer_days=draft.record.post_test_buffer_days,
        planned_test_start_date=draft.record.planned_test_start_date,
        planned_test_complete_date=draft.record.planned_test_complete_date,
        estimated_completion_date=draft.record.estimated_completion_date,
        groups=tuple(
            MatrixEditorSessionGroup(
                draft_group_id=group.draft_group_id,
                source_group_snapshot_id=group.source_group_snapshot_id,
                group_order=group.group_order,
                group_key=group.group_key,
                group_label=group.group_label,
                is_selected=group.is_selected,
                sample_quantity_expression=group.sample_quantity_expression,
                sample_note=group.sample_note,
            )
            for group in draft.groups
        ),
        rows=tuple(
            MatrixEditorSessionRow(
                draft_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                row_order=row.row_order,
                test_item=row.test_item,
                source_section=row.source_section,
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
                is_sample_row=row.is_sample_row,
            )
            for row in draft.rows
        ),
        cells=tuple(
            MatrixEditorSessionCell(
                draft_row_id=cell.draft_row_id,
                draft_group_id=cell.draft_group_id,
                cell_value=cell.cell_value,
            )
            for cell in draft.cells
        ),
    )


def _build_active_snapshot(sample_quantity_expression: str = "5") -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-05-27T00:00:00Z",
            post_test_buffer_days="0",
            planned_test_start_date="2026-09-01",
            planned_test_complete_date="2026-09-01",
            estimated_completion_date="2026-09-01",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression=sample_quantity_expression,
                sample_note=None,
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id="cr-1",
                confirmed_matrix_id="cmv-1",
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
            ),
        ),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cc-1",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cr-1",
                confirmed_group_id="cg-1",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
