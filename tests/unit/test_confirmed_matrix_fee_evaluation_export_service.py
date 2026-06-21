from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import json
from pathlib import Path

import pytest

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftError,
    ConfirmedMatrixFeeDraftNotFoundError,
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationHeader,
    FeeEvaluationLineItem,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ConfirmedMatrixFeeEvaluationExportService,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedManualRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.project_output_record_service import (
    ProjectOutputStatusItem,
    ProjectOutputStatusSummary,
    RegisterProjectOutputCommand,
)
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)
from backend.infrastructure.office.models import FeeEvaluationWorkbookWriteResult


def test_ready_draft_exports_and_registers_fee_output_record(tmp_path: Path) -> None:
    template = _template(tmp_path)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    output_service = _OutputService()
    writer = _Writer()
    service = _service(
        draft=_draft(status="ready", total_fee=Decimal("100")),
        output_service=output_service,
        writer=writer,
    )

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=template,
            output_dir=output_dir,
            connlab_user="ConnLab Operator",
            approved_by="Lead",
        )
    )

    assert result.output_path == output_dir / "P1_fee_evaluation_1_fee_rules_v2026_06_03.xls"
    assert result.output_format == "xls"
    assert result.status == "generated"
    assert result.prepared_by == "ConnLab Operator"
    assert result.approved_by == "Lead"
    assert result.output_record_id == "por-1"
    assert result.line_traceability[0].line_id == "line-1"
    assert result.line_traceability[0].confirmed_group_id == "cmg-1"
    assert result.line_traceability[0].confirmed_row_id == "cmr-1"
    assert result.line_traceability[0].matched_rule_id == "fee_rule_fixture"
    assert result.line_traceability[0].matched_rule_version_id == (
        "fee_rules_v2026_06_03"
    )
    assert writer.calls[0].draft.header.confirmed_matrix_id == "cmv-1"
    command = output_service.commands[0]
    assert command.output_kind is ProjectOutputKind.FEE_EVALUATION
    assert command.status is ProjectOutputStatus.CURRENT
    assert command.source is ProjectOutputSource.SYSTEM_GENERATED
    assert command.draft_id == "D1"
    assert "confirmed_matrix_id=cmv-1" in (command.note or "")
    assert "fee_rule_version_id=fee_rules_v2026_06_03" in (command.note or "")
    assert "line_id=line-1" in (command.note or "")
    assert "confirmed_group_id=cmg-1" in (command.note or "")
    assert "confirmed_row_id=cmr-1" in (command.note or "")
    assert "matched_rule_id=fee_rule_fixture" in (command.note or "")
    assert "matched_rule_version_id=fee_rules_v2026_06_03" in (command.note or "")


def test_needs_review_draft_is_rejected_by_default(tmp_path: Path) -> None:
    service = _service(draft=_draft(status="needs_review"))

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="requires review"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
            )
        )


def test_allow_review_required_passes_draft_to_writer(tmp_path: Path) -> None:
    template = _template(tmp_path)
    writer = _Writer()
    service = _service(draft=_draft(status="needs_review"), writer=writer)

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=template,
            output_dir=tmp_path,
            allow_review_required=True,
        )
    )

    assert result.status == "generated"
    assert writer.calls[0].draft.draft_status == "needs_review"
    assert "Approval remains manual." in result.warnings


def test_matrix_basic_fill_is_explicit_and_allows_review_required_draft(
    tmp_path: Path,
) -> None:
    template = _template(tmp_path)
    writer = _Writer()
    output_service = _OutputService()
    service = _service(
        draft=_draft(status="needs_review"),
        output_service=output_service,
        writer=writer,
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=template,
            output_dir=tmp_path,
            fill_mode="matrix_basic",
        )
    )

    assert result.status == "generated"
    assert writer.basic_calls[0].basic_fill.groups[0].lines[0].test_item == (
        "Visual Examination"
    )
    assert writer.basic_calls[0].basic_fill.groups[0].lines[1].cell_value == "abc"
    assert "Matrix basic fill only." in result.warnings
    note = output_service.commands[0].note or ""
    assert "fill_mode=matrix_basic" in note
    assert "pricing_requires_review=true" in note
    assert "confirmed_row_id=cmr-llcr" in note
    assert 'cell_value="abc"' in note
    assert result.line_traceability[1].cell_value == "abc"


def test_matrix_basic_fill_note_json_encodes_source_cell_value(
    tmp_path: Path,
) -> None:
    output_service = _OutputService()
    raw_cell_value = "1, X; =bad\nnext"
    service = _service(
        draft=_draft(status="needs_review"),
        output_service=output_service,
        confirmed_store=_ConfirmedStore(
            _basic_snapshot(second_cell_value=raw_cell_value)
        ),
    )

    service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
            fill_mode="matrix_basic",
        )
    )

    note = output_service.commands[0].note or ""
    assert f"cell_value={json.dumps(raw_cell_value)}" in note


def test_matrix_basic_fill_does_not_require_fee_draft_success(
    tmp_path: Path,
) -> None:
    template = _template(tmp_path)
    writer = _Writer()
    output_service = _OutputService()
    service = ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=_FailingDraftService(),
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
        project_output_service=output_service,
        workbook_writer=writer,
    )

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=template,
            output_dir=tmp_path,
            fill_mode="matrix_basic",
        )
    )

    assert result.status == "generated"
    assert writer.basic_calls[0].basic_fill.groups[0].lines[1].cell_value == "abc"
    assert writer.basic_calls[0].review_required is True
    assert "Fee draft review metadata is unavailable." in result.warnings
    note = output_service.commands[0].note or ""
    assert "pricing_requires_review=true" in note
    assert 'cell_value="abc"' in note


def test_matrix_basic_fill_download_does_not_require_active_output_draft(
    tmp_path: Path,
) -> None:
    output_service = _OutputService(active_draft_id=None)
    service = _service(
        draft=_draft(status="needs_review"),
        output_service=output_service,
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
            fill_mode="matrix_basic",
        )
    )

    assert result.status == "generated"
    assert result.output_record_id is None
    assert output_service.commands == []
    assert (
        "Fee output record was not registered because no active reviewed draft exists."
        in result.warnings
    )


def test_matrix_basic_fill_passes_edited_values_to_writer(tmp_path: Path) -> None:
    writer = _Writer()
    service = _service(
        draft=_draft(status="needs_review"),
        writer=writer,
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )
    edited_values = _edited_values(_edited_visual_row())

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
            fill_mode="matrix_basic",
            edited_values=edited_values,
        )
    )

    assert result.status == "generated"
    assert writer.basic_calls[0].edited_values == edited_values


def test_matrix_basic_fill_passes_basic_information_values_to_writer(
    tmp_path: Path,
) -> None:
    writer = _Writer()
    service = _service(
        draft=_draft(status="needs_review"),
        writer=writer,
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
            fill_mode="matrix_basic",
            basic_information_values={
                "dl_number": "DL-BI",
                "product_description": "Connector from Basic Information",
                "test_item": "Qualification test",
                "requested_by": "Requester BI",
                "location": "Dongguan",
                "lab_performing_tests": "Dongguan",
            },
        )
    )

    assert result.status == "generated"
    assert writer.basic_calls[0].basic_information_values == {
        "dl_number": "DL-BI",
        "product_description": "Connector from Basic Information",
        "test_item": "Qualification test",
        "requested_by": "Requester BI",
        "location": "Dongguan",
        "lab_performing_tests": "Dongguan",
    }


def test_matrix_basic_fill_rejects_duplicate_edited_row_identity(tmp_path: Path) -> None:
    service = _service(
        draft=_draft(status="needs_review"),
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )
    edited_values = _edited_values(_edited_visual_row(), _edited_visual_row())

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="Duplicate"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
                fill_mode="matrix_basic",
                edited_values=edited_values,
            )
        )


def test_matrix_basic_fill_rejects_unknown_edited_row_identity(tmp_path: Path) -> None:
    service = _service(
        draft=_draft(status="needs_review"),
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )
    edited_values = _edited_values(
        FeeEvaluationEditedExportRow(
            source_line_id="cmv-1:g1:unknown:1:0",
            confirmed_group_id="cmg-1",
            confirmed_row_id="unknown",
            step_token="1",
            step_index=0,
            spend_time="1",
            unit_price="10",
            unit_type="per sample",
            units="1",
            base_fee="0",
            discount="0%",
            testing_fee="10",
            notes="",
        )
    )

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="not found"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
                fill_mode="matrix_basic",
                edited_values=edited_values,
            )
        )


def test_matrix_basic_fill_rejects_incomplete_sample_preparation_identity(
    tmp_path: Path,
) -> None:
    service = _service(
        draft=_draft(status="needs_review"),
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )
    edited_values = FeeEvaluationEditedExportValues(
        rows=(),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0",
            external_cost="0",
            external_cost_note="",
            lab_manpower_hourly_rate="200",
        ),
        manual_rows=(
            FeeEvaluationEditedManualRow(
                row_kind="sample_preparation",
                confirmed_group_id="cmg-1",
                group_key="g1",
                group_label="",
                spend_time="0",
                unit_price="0",
                unit_type="per sample",
                units="1",
                base_fee="0",
                discount="0%",
                testing_fee="0",
                notes="",
            ),
        ),
    )

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="complete group identity"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
                fill_mode="matrix_basic",
                edited_values=edited_values,
            )
        )


def test_matrix_basic_fill_allows_missing_edited_rows(tmp_path: Path) -> None:
    writer = _Writer()
    service = _service(
        draft=_draft(status="needs_review"),
        writer=writer,
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )

    service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
            fill_mode="matrix_basic",
            edited_values=_edited_values(),
        )
    )

    assert writer.basic_calls[0].edited_values is not None


def test_matrix_basic_fill_propagates_unexpected_fee_draft_errors(
    tmp_path: Path,
) -> None:
    service = ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=_BuggyDraftService(),
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
        project_output_service=_OutputService(),
        workbook_writer=_Writer(),
    )

    with pytest.raises(TypeError, match="programming bug"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
                fill_mode="matrix_basic",
            )
        )


def test_matrix_basic_fill_marks_pricing_review_when_authority_has_basic_only_lines(
    tmp_path: Path,
) -> None:
    writer = _Writer()
    output_service = _OutputService()
    service = _service(
        draft=_draft(status="ready", total_fee=Decimal("100")),
        output_service=output_service,
        writer=writer,
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
            fill_mode="matrix_basic",
        )
    )

    assert result.status == "generated"
    assert writer.basic_calls[0].review_required is True
    assert "Pricing still requires review." in result.warnings
    assert "Matrix basic fill includes rows not present in fee draft." in result.warnings
    assert "pricing_requires_review=true" in (output_service.commands[0].note or "")


def test_default_export_mode_still_rejects_needs_review_draft(
    tmp_path: Path,
) -> None:
    service = _service(
        draft=_draft(status="needs_review"),
        confirmed_store=_ConfirmedStore(_basic_snapshot()),
    )

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="requires review"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
            )
        )


def test_existing_output_rejected_without_overwrite(tmp_path: Path) -> None:
    template = _template(tmp_path)
    target = tmp_path / "fee.xls"
    target.write_text("existing", encoding="utf-8")
    service = _service(draft=_draft(status="ready", total_fee=Decimal("100")))

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="already exists"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=template,
                output_dir=tmp_path,
                output_file_name="fee.xls",
            )
        )


def test_prepared_by_falls_back_to_os_user_and_approved_by_stays_blank(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.confirmed_matrix_fee_evaluation_export_service.getpass.getuser",
        lambda: "windows-user",
    )
    writer = _Writer()
    service = _service(draft=_draft(status="ready", total_fee=Decimal("100")), writer=writer)

    result = service.export(
        ExportConfirmedMatrixFeeEvaluationCommand(
            project_id="P1",
            template_path=_template(tmp_path),
            output_dir=tmp_path,
        )
    )

    assert result.prepared_by == "windows-user"
    assert result.approved_by is None
    assert writer.calls[0].prepared_by == "windows-user"
    assert writer.calls[0].approved_by is None
    assert "Approval remains manual." in result.warnings


def test_missing_active_output_draft_blocks_current_record_registration(
    tmp_path: Path,
) -> None:
    output_service = _OutputService(active_draft_id=None)
    service = _service(
        draft=_draft(status="ready", total_fee=Decimal("100")),
        output_service=output_service,
    )

    with pytest.raises(ConfirmedMatrixFeeEvaluationExportError, match="active reviewed draft"):
        service.export(
            ExportConfirmedMatrixFeeEvaluationCommand(
                project_id="P1",
                template_path=_template(tmp_path),
                output_dir=tmp_path,
            )
        )


def _service(
    *,
    draft: FeeEvaluationDraft,
    output_service: _OutputService | None = None,
    writer: _Writer | None = None,
    confirmed_store: "_ConfirmedStore | None" = None,
) -> ConfirmedMatrixFeeEvaluationExportService:
    return ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=_DraftService(draft),
        confirmed_store=confirmed_store or _ConfirmedStore(_basic_snapshot()),
        project_output_service=output_service or _OutputService(),
        workbook_writer=writer or _Writer(),
    )


def _template(tmp_path: Path) -> Path:
    template = tmp_path / "template.xls"
    template.write_text("template", encoding="utf-8")
    return template


def _edited_values(
    *rows: FeeEvaluationEditedExportRow,
) -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=rows,
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0",
            external_cost="0",
            external_cost_note="",
            lab_manpower_hourly_rate="200",
        ),
    )


def _edited_visual_row() -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id="cmv-1:g1:cmr-visual:1:0",
        confirmed_group_id="cmg-1",
        confirmed_row_id="cmr-visual",
        step_token="1",
        step_index=0,
        spend_time="1",
        unit_price="10",
        unit_type="per sample",
        units="2",
        base_fee="5",
        discount="10%",
        testing_fee="23",
        notes="special discount",
    )


def _draft(
    *,
    status: str,
    total_fee: Decimal | None = None,
) -> FeeEvaluationDraft:
    line = FeeEvaluationLineItem(
        line_id="line-1",
        status="calculated" if status == "ready" else "review_required",
        review_required=status != "ready",
        review_reason=None if status == "ready" else "Manual review required.",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        group_key="g1",
        group_label="Group 1",
        confirmed_group_id="cmg-1",
        sample_quantity_expression="1",
        spend_time="2D",
        confirmed_row_id="cmr-1",
        source_row_id="smr-1",
        row_order=1,
        test_item="Fixture setup",
        section="6.1",
        method="Fixture",
        condition="",
        requirement="",
        step_tokens=("1",),
        matched_rule_id="fee_rule_fixture",
        matched_rule_version_id="fee_rules_v2026_06_03",
        matched_rule_name="Fixture setup",
        match_reason="exact",
        calculation_strategy="fixed_per_group",
        unit_label="group",
        unit_price=Decimal("100"),
        units=Decimal("1") if status == "ready" else None,
        base_fee=Decimal("0"),
        discount_percent=Decimal("0"),
        testing_fee=total_fee,
        warnings=(),
    )
    return FeeEvaluationDraft(
        header=FeeEvaluationHeader(
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            pricing_rule_version_id="fee_rules_v2026_06_03",
            pricing_source_file_name="Testing Fee Evaluation-Even.xls",
            pricing_source_hash="sha256:abc",
            pricing_effective_from="2026-06-03",
            generated_at="2026-06-04T10:00:00+08:00",
        ),
        draft_status=status,
        total_fee=total_fee,
        review_required_count=0 if status == "ready" else 1,
        groups=(
            FeeEvaluationGroup(
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="1",
                line_items=(line,),
            ),
        ),
        warnings=(),
    )


class _DraftService:
    def __init__(self, draft: FeeEvaluationDraft) -> None:
        self.draft = draft
        self.commands: list[BuildConfirmedMatrixFeeDraftCommand] = []

    def build_draft(self, command: BuildConfirmedMatrixFeeDraftCommand) -> FeeEvaluationDraft:
        self.commands.append(command)
        return self.draft


class _FailingDraftService:
    def build_draft(self, command: BuildConfirmedMatrixFeeDraftCommand) -> FeeEvaluationDraft:
        raise ConfirmedMatrixFeeDraftError("Fee draft cannot be built.")


class _BuggyDraftService:
    def build_draft(self, command: BuildConfirmedMatrixFeeDraftCommand) -> FeeEvaluationDraft:
        raise TypeError("programming bug")


@dataclass(frozen=True, slots=True)
class _WriteCall:
    template_path: Path
    output_path: Path
    draft: FeeEvaluationDraft
    prepared_by: str | None
    approved_by: str | None


@dataclass(frozen=True, slots=True)
class _BasicWriteCall:
    template_path: Path
    output_path: Path
    basic_fill: object
    review_required: bool
    prepared_by: str | None
    approved_by: str | None
    edited_values: FeeEvaluationEditedExportValues | None
    basic_information_values: dict[str, str] | None


class _Writer:
    def __init__(self) -> None:
        self.calls: list[_WriteCall] = []
        self.basic_calls: list[_BasicWriteCall] = []

    def generate_from_draft(
        self,
        *,
        template_path: Path,
        output_path: Path,
        draft: FeeEvaluationDraft,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        self.calls.append(
            _WriteCall(
                template_path=template_path,
                output_path=output_path,
                draft=draft,
                prepared_by=prepared_by,
                approved_by=approved_by,
            )
        )
        output_path.write_text("generated", encoding="utf-8")
        return FeeEvaluationWorkbookWriteResult(
            output_path=output_path,
            status="generated",
            warnings=(),
        )

    def generate_matrix_basic_fill(
        self,
        *,
        template_path: Path,
        output_path: Path,
        basic_fill: object,
        review_required: bool,
        prepared_by: str | None,
        approved_by: str | None,
        edited_values: FeeEvaluationEditedExportValues | None = None,
        basic_information_values: dict[str, str] | None = None,
    ) -> FeeEvaluationWorkbookWriteResult:
        self.basic_calls.append(
            _BasicWriteCall(
                template_path=template_path,
                output_path=output_path,
                basic_fill=basic_fill,
                review_required=review_required,
                prepared_by=prepared_by,
                approved_by=approved_by,
                edited_values=edited_values,
                basic_information_values=basic_information_values,
            )
        )
        output_path.write_text("generated-basic", encoding="utf-8")
        return FeeEvaluationWorkbookWriteResult(
            output_path=output_path,
            status="generated",
            warnings=("Matrix basic fill only.",),
        )


class _OutputService:
    def __init__(self, active_draft_id: str | None = "D1") -> None:
        self.active_draft_id = active_draft_id
        self.commands: list[RegisterProjectOutputCommand] = []

    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        return ProjectOutputStatusSummary(
            project_id=project_id,
            active_draft_id=self.active_draft_id,
            active_draft_version=1 if self.active_draft_id else None,
            items=(
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.FEE_EVALUATION,
                    status=ProjectOutputStatus.MISSING,
                    output_path=None,
                    source=None,
                    draft_id=None,
                    draft_version=None,
                    reason="No persisted output record exists.",
                    updated_at=None,
                ),
            ),
        )

    def register_output(
        self, command: RegisterProjectOutputCommand
    ) -> object:
        self.commands.append(command)
        return type("Record", (), {"output_record_id": "por-1"})()


class _ConfirmedStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot | None) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot


def _basic_snapshot(*, second_cell_value: str = "abc") -> ConfirmedMatrixSnapshot:
    visual = ConfirmedMatrixRow(
        confirmed_row_id="cmr-visual",
        confirmed_matrix_id="cmv-1",
        draft_row_id="pmdr-visual",
        source_row_snapshot_id="smr-visual",
        row_order=1,
        test_item="Visual Examination",
    )
    llcr = ConfirmedMatrixRow(
        confirmed_row_id="cmr-llcr",
        confirmed_matrix_id="cmv-1",
        draft_row_id="pmdr-llcr",
        source_row_snapshot_id="smr-llcr",
        row_order=2,
        test_item="LLCR",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="cmg-1",
        confirmed_matrix_id="cmv-1",
        draft_group_id="pmdg-1",
        source_group_snapshot_id="smg-1",
        group_order=1,
        group_key="g1",
        group_label="Group 1",
        sample_quantity_expression="5",
    )
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
            confirmed_at="2026-06-04T10:00:00+08:00",
            sample_received_date="2026-06-03",
        ),
        groups=(group,),
        rows=(visual, llcr),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-visual",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id=visual.confirmed_row_id,
                confirmed_group_id=group.confirmed_group_id,
                draft_row_id=visual.draft_row_id,
                draft_group_id=group.draft_group_id,
                cell_value="1 X",
            ),
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-llcr",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id=llcr.confirmed_row_id,
                confirmed_group_id=group.confirmed_group_id,
                draft_row_id=llcr.draft_row_id,
                draft_group_id=group.draft_group_id,
                cell_value=second_cell_value,
            ),
        ),
    )
