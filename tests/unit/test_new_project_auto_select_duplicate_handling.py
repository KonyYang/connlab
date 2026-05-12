"""Tests for New Project auto-select duplicate handling (Phase 1.1 fixes).

These tests verify the fixes for contradiction 2:
- Auto-select should gracefully skip duplicates without creating separate drafts implicitly
- Auto-select should reuse existing case with selected form
- Auto-select should not throw unexpected exceptions during page load
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import cast
from unittest.mock import MagicMock, create_autospec

import pytest

from backend.application.intake_form_selection_service import (
    FormSelectionResult,
    IntakeDraftDuplicateResolutionRequiredError,
    IntakeSelectionError,
)
from backend.application.new_project_application_draft_service import (
    NewProjectApplicationDraftService,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)


class TestAutoSelectReusesExistingCaseWithForm:
    """Tests that auto-select reuses an existing case that already has a selected form."""

    def test_reuses_existing_case_with_selected_form(self):
        """When a reusable case with selected_form_asset_id exists, it should be reused."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        existing_case = IntakeCase(
            case_id="case-existing-001",
            package_id=package_id,
            selected_form_asset_id="asset-form-001",
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        existing_draft = IntakeDraft(
            draft_id="draft-001",
            case_id=existing_case.case_id,
            parsed_fields_json=json.dumps({"field": "value"}),
            parser_warnings_json=json.dumps([]),
        )

        # Mock: case exists with selected form
        case_store.list_by_package.return_value = [existing_case]
        draft_store.get_by_case.return_value = existing_draft

        # Act - call the method directly via ensure_draft
        result = service._auto_select_application_form(package_id)

        # Assert
        assert result is not None
        case, draft = result
        assert case.case_id == existing_case.case_id
        assert case.selected_form_asset_id == "asset-form-001"
        assert draft.draft_id == existing_draft.draft_id

        # Verify selection_service was never called (no re-parsing)
        selection_service.select_form_asset.assert_not_called()

    def test_does_not_reuse_case_without_selected_form(self):
        """Cases without selected_form_asset_id should not be reused for auto-select."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        existing_case_no_form = IntakeCase(
            case_id="case-existing-001",
            package_id=package_id,
            selected_form_asset_id=None,  # No form selected
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        word_asset = IntakeAsset(
            asset_id="asset-docx-001",
            package_id=package_id,
            original_name="application.docx",
            stored_path="/path/to/docx",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="abc123",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )
        selection_result = FormSelectionResult(
            package_id=package_id,
            case=IntakeCase(
                case_id="case-new-001",
                package_id=package_id,
                selected_form_asset_id=word_asset.asset_id,
                status=IntakeCaseStatus.NEEDS_REVIEW,
            ),
            draft=IntakeDraft(
                draft_id="draft-new-001",
                case_id="case-new-001",
                parsed_fields_json=json.dumps({}),
                parser_warnings_json=json.dumps([]),
            ),
            selected_asset=word_asset,
        )

        # Mock: case exists but no form selected, and there's a word asset
        case_store.list_by_package.return_value = [existing_case_no_form]
        asset_store.list_by_package.return_value = [word_asset]
        selection_service.select_form_asset.return_value = selection_result

        # Act
        result = service._auto_select_application_form(package_id)

        # Assert
        assert result is not None
        case, draft = result
        assert case.case_id == "case-new-001"  # New case created via selection

        # Verify selection_service was called (needed to select a form)
        selection_service.select_form_asset.assert_called_once()
        call_kwargs = selection_service.select_form_asset.call_args[1]
        assert "resolution_action" not in call_kwargs


class TestAutoSelectGracefullySkipsDuplicates:
    """Tests that auto-select gracefully skips duplicate candidates."""

    def test_does_not_pass_create_separate_resolution_action(self):
        """Auto-select must not create separate drafts implicitly."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        word_asset = IntakeAsset(
            asset_id="asset-docx-001",
            package_id=package_id,
            original_name="application.docx",
            stored_path="/path/to/docx",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="abc123",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )
        selection_result = FormSelectionResult(
            package_id=package_id,
            case=IntakeCase(
                case_id="case-001",
                package_id=package_id,
                selected_form_asset_id=word_asset.asset_id,
                status=IntakeCaseStatus.NEEDS_REVIEW,
            ),
            draft=IntakeDraft(
                draft_id="draft-001",
                case_id="case-001",
                parsed_fields_json=json.dumps({}),
                parser_warnings_json=json.dumps([]),
            ),
            selected_asset=word_asset,
        )

        # Mock: no existing case, has word asset
        case_store.list_by_package.return_value = []
        asset_store.list_by_package.return_value = [word_asset]
        selection_service.select_form_asset.return_value = selection_result

        # Act
        result = service._auto_select_application_form(package_id)

        # Assert
        assert result is not None
        selection_service.select_form_asset.assert_called_once_with(
            package_id,
            word_asset.asset_id,
        )

    def test_skips_duplicate_and_tries_next_candidate(self):
        """When one candidate triggers duplicate, should try next candidate."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        asset1 = IntakeAsset(
            asset_id="asset-docx-001",
            package_id=package_id,
            original_name="application1.docx",
            stored_path="/path/to/docx1",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="abc123",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )
        asset2 = IntakeAsset(
            asset_id="asset-docx-002",
            package_id=package_id,
            original_name="application2.docx",
            stored_path="/path/to/docx2",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="def456",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )
        selection_result = FormSelectionResult(
            package_id=package_id,
            case=IntakeCase(
                case_id="case-002",
                package_id=package_id,
                selected_form_asset_id=asset2.asset_id,
                status=IntakeCaseStatus.NEEDS_REVIEW,
            ),
            draft=IntakeDraft(
                draft_id="draft-002",
                case_id="case-002",
                parsed_fields_json=json.dumps({}),
                parser_warnings_json=json.dumps([]),
            ),
            selected_asset=asset2,
        )

        # Mock: asset1 triggers duplicate resolution error; asset2 succeeds.
        case_store.list_by_package.return_value = []
        asset_store.list_by_package.return_value = [asset1, asset2]

        def side_effect(pkg_id, asset_id, **kwargs):
            if asset_id == asset1.asset_id:
                raise IntakeDraftDuplicateResolutionRequiredError(
                    MagicMock(
                        classification="exact_existing_application_draft",
                        existing_case_id="case-existing",
                    )
                )
            return selection_result

        selection_service.select_form_asset.side_effect = side_effect

        # Act - should NOT raise, should try next candidate
        result = service._auto_select_application_form(package_id)

        # Assert
        assert result is not None
        case, draft = result
        assert case.case_id == "case-002"  # From asset2
        assert selection_service.select_form_asset.call_count == 2

    def test_returns_none_when_all_candidates_fail(self):
        """When all candidates fail, should return None gracefully."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        word_asset = IntakeAsset(
            asset_id="asset-docx-001",
            package_id=package_id,
            original_name="application.docx",
            stored_path="/path/to/docx",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="abc123",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )

        # Mock: no existing case, has word asset but it fails
        case_store.list_by_package.return_value = []
        asset_store.list_by_package.return_value = [word_asset]
        selection_service.select_form_asset.side_effect = IntakeSelectionError(
            "Not eligible"
        )

        # Act - should NOT raise
        result = service._auto_select_application_form(package_id)

        # Assert
        assert result is None


class TestAutoSelectDoesNotThrowUnexpectedExceptions:
    """Tests that auto-select does not throw unexpected exceptions during page load."""

    def test_does_not_raise_duplicate_resolution_error(self):
        """Even when duplicate is detected, should not raise exception to caller."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        word_asset = IntakeAsset(
            asset_id="asset-docx-001",
            package_id=package_id,
            original_name="application.docx",
            stored_path="/path/to/docx",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="abc123",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )

        # Mock: no existing case, has word asset but triggers duplicate
        case_store.list_by_package.return_value = []
        asset_store.list_by_package.return_value = [word_asset]
        selection_service.select_form_asset.side_effect = (
            IntakeDraftDuplicateResolutionRequiredError(
                MagicMock(
                    classification="exact_existing_application_draft",
                    existing_case_id="case-existing",
                    existing_package_id="pkg-existing",
                )
            )
        )

        # Act & Assert - should NOT raise
        try:
            result = service._auto_select_application_form(package_id)
            # Should return None gracefully
            assert result is None
        except IntakeDraftDuplicateResolutionRequiredError:
            pytest.fail(
                "Should not raise IntakeDraftDuplicateResolutionRequiredError during auto-select"
            )

    def test_ensure_draft_does_not_raise_on_auto_select_duplicate(self):
        """ensure_draft should complete successfully even when auto-select hits duplicate."""
        # Arrange
        package_store = MagicMock()
        case_store = MagicMock()
        draft_store = MagicMock()
        asset_store = MagicMock()
        selection_service = MagicMock()

        service = NewProjectApplicationDraftService(
            package_store=package_store,
            case_store=case_store,
            draft_store=draft_store,
            asset_store=asset_store,
            selection_service=selection_service,
        )

        package_id = "pkg-test-001"
        from pathlib import Path
        package = IntakePackage(
            package_id=package_id,
            source_type=IntakePackageSourceType.OUTLOOK_MSG,
            status=IntakePackageStatus.IMPORTED,
            source_original_name="test.msg",
            source_stored_path=Path("/path/to/msg"),
        )
        word_asset = IntakeAsset(
            asset_id="asset-docx-001",
            package_id=package_id,
            original_name="application.docx",
            stored_path="/path/to/docx",
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=1024,
            sha256="abc123",
            asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
        )
        blank_case = IntakeCase(
            case_id="case-blank-001",
            package_id=package_id,
            selected_form_asset_id=None,
            status=IntakeCaseStatus.NEEDS_REVIEW,
        )
        blank_draft = IntakeDraft(
            draft_id="draft-blank-001",
            case_id=blank_case.case_id,
            parsed_fields_json=json.dumps({}),
            parser_warnings_json=json.dumps([]),
        )

        # Mock: package exists, auto-select hits duplicate, falls back to blank
        package_store.get.return_value = package
        package_store.update.return_value = package
        case_store.list_by_package.return_value = []
        asset_store.list_by_package.return_value = [word_asset]
        selection_service.select_form_asset.side_effect = (
            IntakeDraftDuplicateResolutionRequiredError(
                MagicMock(
                    classification="exact_existing_application_draft",
                    existing_case_id="case-existing",
                    existing_package_id="pkg-existing",
                )
            )
        )
        # No-form duplicate check returns None
        asset_store.list_by_package.side_effect = [
            [word_asset],  # First call for auto-select
            [],  # Second call for _email_source_asset
        ]
        # Create blank draft
        case_store.create.return_value = blank_case
        draft_store.get_by_case.return_value = None
        draft_store.create.return_value = blank_draft

        # Act & Assert - should NOT raise
        try:
            result = service.ensure_draft(package_id)
            # Should return blank draft
            assert result.case.case_id == blank_case.case_id
            assert result.draft.draft_id == blank_draft.draft_id
        except IntakeDraftDuplicateResolutionRequiredError:
            pytest.fail(
                "ensure_draft should not raise IntakeDraftDuplicateResolutionRequiredError"
            )
