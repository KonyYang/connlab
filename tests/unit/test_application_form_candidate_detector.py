from pathlib import Path

from backend.application.intake_candidate_service import ApplicationFormCandidateDetector
from backend.domain import IntakeAsset, IntakeAssetRole


class InMemoryAssetStore:
    def __init__(self, assets: list[IntakeAsset]) -> None:
        self.assets = {asset.asset_id: asset for asset in assets}

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        return [asset for asset in self.assets.values() if asset.package_id == package_id]

    def update(self, asset: IntakeAsset) -> IntakeAsset:
        self.assets[asset.asset_id] = asset
        return asset


def _asset(asset_id: str, name: str, extension: str, role: IntakeAssetRole) -> IntakeAsset:
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name=name,
        stored_path=Path(f"data/intake/pkg-1/attachments/{name}"),
        extension=extension,
        mime_type="application/octet-stream",
        size_bytes=100,
        sha256=asset_id * 64,
        asset_role=role,
    )


def test_detector_scores_word_application_form_as_candidate() -> None:
    store = InMemoryAssetStore(
        [
            _asset("a", "E-3718 Application Form.docx", ".docx", IntakeAssetRole.UNKNOWN),
            _asset("b", "connector drawing.pdf", ".pdf", IntakeAssetRole.UNKNOWN),
        ]
    )

    result = ApplicationFormCandidateDetector(store).detect_for_package("pkg-1")

    assert result.reviewed_asset_count == 2
    assert [candidate.asset_id for candidate in result.candidates] == ["a"]
    assert store.assets["a"].asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE
    assert store.assets["b"].asset_role is IntakeAssetRole.SUPPORTING_ATTACHMENT


def test_detector_keeps_human_selected_and_ignored_roles_protected() -> None:
    store = InMemoryAssetStore(
        [
            _asset("a", "old selection.docx", ".docx", IntakeAssetRole.SELECTED_APPLICATION_FORM),
            _asset("b", "application form.docx", ".docx", IntakeAssetRole.IGNORED),
        ]
    )

    result = ApplicationFormCandidateDetector(store).detect_for_package("pkg-1")

    assert result.candidates == ()
    assert store.assets["a"].asset_role is IntakeAssetRole.SELECTED_APPLICATION_FORM
    assert store.assets["b"].asset_role is IntakeAssetRole.IGNORED


def test_detector_penalizes_non_application_word_documents() -> None:
    store = InMemoryAssetStore(
        [_asset("a", "test result report.docx", ".docx", IntakeAssetRole.UNKNOWN)]
    )

    result = ApplicationFormCandidateDetector(store).detect_for_package("pkg-1")

    assert result.candidates == ()
    assert store.assets["a"].asset_role is IntakeAssetRole.SUPPORTING_ATTACHMENT
