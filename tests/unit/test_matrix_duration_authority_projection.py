from dataclasses import replace
from decimal import Decimal

import pytest

from backend.application.matrix_revision_snapshot_builder import (
    build_confirmed_duration_authorities,
    carry_forward_duration_authorities,
)
from backend.application.source_matrix_import_builder import prepare_source_matrix_import
from backend.domain import (
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)
from backend.domain.confirmed_matrix_authority_models import (
    ConfirmedMatrixDurationAuthority,
)


def test_revision_carry_forward_and_confirm_preserve_typed_duration_facts() -> None:
    active = _confirmed_snapshot()
    draft_items = carry_forward_duration_authorities(
        active=active,
        draft_id="draft-2",
        group_id_map={"group-1": "draft-group-2"},
        row_id_map={"row-1": "draft-row-2"},
        updated_at="2026-07-24T09:00:00+00:00",
    )
    assert len(draft_items) == 1
    assert (draft_items[0].duration_value, draft_items[0].normalized_hours) == (
        Decimal("2"),
        Decimal("48"),
    )
    assert draft_items[0].lineage_fingerprint == "lineage-fp"

    draft = ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="draft-2",
            project_id="P1",
            source_import_id="import-1",
            source_snapshot_id="source-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-24T09:00:00+00:00",
            updated_at="2026-07-24T09:00:00+00:00",
            base_confirmed_matrix_id="matrix-1",
        ),
        duration_authorities=draft_items,
    )
    published = build_confirmed_duration_authorities(
        draft=draft,
        confirmed_matrix_id="matrix-2",
        confirmed_at="2026-07-24T10:00:00+00:00",
        confirmed_group_id_by_draft_group={"draft-group-2": "group-2"},
        confirmed_row_id_by_draft_row={"draft-row-2": "row-2"},
    )
    assert len(published) == 1
    assert published[0].confirmed_group_id == "group-2"
    assert published[0].confirmed_row_id == "row-2"
    assert published[0].normalized_hours == Decimal("48")


def test_revision_carry_forward_fails_closed_on_missing_identity() -> None:
    with pytest.raises(ValueError, match="lineage is incomplete"):
        carry_forward_duration_authorities(
            active=_confirmed_snapshot(),
            draft_id="draft-2",
            group_id_map={},
            row_id_map={"row-1": "draft-row-2"},
            updated_at="2026-07-24T09:00:00+00:00",
        )


def test_structured_matrix_edit_step_projects_to_source_authority_without_text_inference() -> None:
    prepared = prepare_source_matrix_import(
        project_id="P1",
        draft_id="test-plan-draft-1",
        source_document_path="C:/disposable/spec.docx",
        source_document_name="spec.docx",
        source_format=".docx",
        source_asset_id=None,
        source_case_id=None,
        source_draft_id=None,
        payload={
            "groups": [
                {
                    "group_key": "g1",
                    "group_label": "G1",
                    "sample_size": 5,
                    "steps": [
                        {
                            "source_row_index": 3,
                            "raw_token": "1",
                            "test_item": "Long-term high temperature zone load",
                            "condition": "Untrusted prose says 999 hours",
                            "duration_authorities": [
                                {
                                    "owning_group_key": "g1",
                                    "step_sequence": 1,
                                    "duration_value": 2,
                                    "duration_unit": "days",
                                    "source_field": "duration_authorities[0]",
                                    "source_identity": {"group_key": "g1"},
                                }
                            ],
                        }
                    ],
                }
            ]
        },
        created_at="2026-07-24T08:00:00+00:00",
        selected_group_keys_override=("g1",),
        task261_commit_fingerprint=None,
    )

    assert len(prepared.snapshot.duration_authorities) == 1
    authority = prepared.snapshot.duration_authorities[0]
    assert authority.duration_value == Decimal("2")
    assert authority.normalized_hours == Decimal("48")
    assert authority.source_field == "duration_authorities[0]"


def _confirmed_snapshot() -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="matrix-1",
            project_id="P1",
            project_matrix_draft_id="draft-1",
            source_import_id="import-1",
            source_snapshot_id="source-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-24T08:00:00+00:00",
        ),
        duration_authorities=(_confirmed_authority(),),
    )


def _confirmed_authority() -> ConfirmedMatrixDurationAuthority:
    return ConfirmedMatrixDurationAuthority(
        confirmed_duration_authority_id="duration-1",
        confirmed_matrix_id="matrix-1",
        confirmed_group_id="group-1",
        confirmed_row_id="row-1",
        step_sequence=1,
        step_suffix_note="",
        duration_value=Decimal("2"),
        duration_unit="days",
        normalized_hours=Decimal("48"),
        source_kind="import_structured",
        source_field="duration_authorities[0]",
        source_import_id="import-1",
        source_fingerprint="source-fp",
        lineage_fingerprint="lineage-fp",
        authority_revision="1",
        status="usable",
        diagnostic_code=None,
        diagnostic_message=None,
        created_at="2026-07-24T08:00:00+00:00",
        updated_at="2026-07-24T08:00:00+00:00",
    )
