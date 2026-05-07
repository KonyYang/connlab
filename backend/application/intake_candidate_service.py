from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from backend.domain import IntakeAsset, IntakeAssetRole


class IntakeAssetStore(Protocol):
    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...

    def update(self, asset: IntakeAsset) -> IntakeAsset: ...


@dataclass(frozen=True)
class ApplicationFormCandidate:
    asset_id: str
    original_name: str
    score: int
    role: IntakeAssetRole
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ApplicationFormCandidateDetectionResult:
    package_id: str
    candidates: tuple[ApplicationFormCandidate, ...]
    reviewed_asset_count: int


class ApplicationFormCandidateDetector:
    """Scores stored intake assets without filename heuristics."""

    _candidate_threshold = 1
    _document_extensions = {".docx"}
    _protected_roles = {
        IntakeAssetRole.EMAIL_SOURCE,
        IntakeAssetRole.SELECTED_APPLICATION_FORM,
        IntakeAssetRole.IGNORED,
    }

    def __init__(self, asset_store: IntakeAssetStore) -> None:
        self._asset_store = asset_store

    def detect_for_package(self, package_id: str) -> ApplicationFormCandidateDetectionResult:
        assets = self._asset_store.list_by_package(package_id)
        reviewed: list[ApplicationFormCandidate] = []

        for asset in assets:
            score, reasons = self.score_asset(asset)
            role = self._role_for(asset, score)
            updated = replace(asset, asset_role=role, candidate_score=score)
            self._asset_store.update(updated)
            if role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE:
                reviewed.append(
                    ApplicationFormCandidate(
                        asset_id=asset.asset_id,
                        original_name=asset.original_name,
                        score=score,
                        role=role,
                        reasons=tuple(reasons),
                    )
                )

        return ApplicationFormCandidateDetectionResult(
            package_id=package_id,
            candidates=tuple(sorted(reviewed, key=lambda item: item.score, reverse=True)),
            reviewed_asset_count=len(assets),
        )

    def score_asset(self, asset: IntakeAsset) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []
        extension = self._normalized_extension(asset)

        if extension in self._document_extensions:
            score = 100
            reasons.append("word_document_extension")
        elif extension:
            reasons.append("non_word_extension")

        if asset.asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE:
            score += 15
            reasons.append("existing_candidate_role")

        return max(0, min(score, 100)), reasons

    def _role_for(self, asset: IntakeAsset, score: int) -> IntakeAssetRole:
        if asset.asset_role in self._protected_roles:
            return asset.asset_role
        if score >= self._candidate_threshold:
            return IntakeAssetRole.APPLICATION_FORM_CANDIDATE
        if asset.asset_role is IntakeAssetRole.UNKNOWN:
            return IntakeAssetRole.SUPPORTING_ATTACHMENT
        return asset.asset_role

    def _normalized_extension(self, asset: IntakeAsset) -> str:
        if asset.extension:
            extension = asset.extension.lower()
        else:
            extension = Path(asset.original_name).suffix.lower()
        if extension and not extension.startswith("."):
            return f".{extension}"
        return extension
